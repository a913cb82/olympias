"""Level-2 equivalence metrics + the equivalence table (the pair contract — simulation/AGENTS.md).

Every metric is computed from the two simulators' 1 Hz telemetry (the snap
dicts from harness/script.py) and checked against the Level-2 first
tolerances:

    |mean speed| < 1 % over the script (sprint + turn included)
    settled stroke rate within 1 spm
    time to 3 NM within 1 % (held course)
    G1/F1 turn diameter within 5 %
    accumulated crew fatigue within 5 %
    final position within ~0.1 NM

The turn diameter metric works on any script whose |psi| crosses 180 deg:
D = |y| at the crossing, linearly interpolated between samples.
"""

from __future__ import annotations

import math

from common.chain import KT

NM = 1852.0  # nautical mile, m
T_3NM = 3.0 * NM


# ---------------------------------------------------------------------------
def _interp_cross(rows, key, target, out_key=None, sign=None):
    """First time |value| >= target (or sign*value >= target if sign given);
    linearly interpolated between the bracketing samples. Returns
    (t_cross, interpolated out_key value) — out_key defaults to key."""
    out_key = key if out_key is None else out_key
    prev = None  # (t, key value, out value)
    for r in rows:
        v = abs(r[key]) if sign is None else sign * r[key]
        if v >= target:
            if prev is None:
                return r["t"], r[out_key]
            t0, v0, o0 = prev
            f = (target - v0) / (v - v0)
            return t0 + f * (r["t"] - t0), o0 + f * (r[out_key] - o0)
        prev = (r["t"], v, r[out_key])
    return None, None


def _cumulative_distance(rows):
    """Track length at each sample, m (1 Hz samples, midpoint rule)."""
    d, out = 0.0, []
    for r in rows:
        d += r["V"] * 1.0
        out.append(d)
    return out


def metrics(ll_rows, hl_rows, exclude_bins=()):
    """The Level-2 metric set; every entry is (ll, hl, tol, unit). The
    position gate is the raw separation (as-written in the pair contract (simulation/AGENTS.md)): the HL
    carries the LL's measured untrimmed drift bias itself (task C, the
    drift-bias decision) — no correction needed here.
    exclude_bins: the per-script scoped 3-min bins (task T5 — the
    cruise_turn back-tail window, the HL's documented domain boundary)."""

    def mean_v(rows):
        # the distance/time integral — the honest mean speed. The
        # sample-mean aliases the low-speed per-stroke surge ripple
        # (the ±40 % oscillation at the back rates: the sampled mean is
        # phase-dependent, the integral is not).
        d = _cumulative_distance(rows)
        t = rows[-1]["t"] - rows[0]["t"]
        return d[-1] / t if t > 0.0 else 0.0

    ll_v, hl_v = mean_v(ll_rows), mean_v(hl_rows)

    d_ll, d_hl = _cumulative_distance(ll_rows), _cumulative_distance(hl_rows)
    t3 = {}
    for name, rows, dist in (("ll", ll_rows, d_ll), ("hl", hl_rows, d_hl)):
        for i, dd in enumerate(dist):
            if dd >= T_3NM:
                if i > 0:
                    f = (T_3NM - dist[i - 1]) / (dd - dist[i - 1])
                    t3[name] = rows[i - 1]["t"] + f * (rows[i]["t"] - rows[i - 1]["t"])
                else:
                    t3[name] = rows[i]["t"]
                break

    end = lambda rows: rows[-1]
    x_ll, y_ll = end(ll_rows)["x"], end(ll_rows)["y"]
    x_hl, y_hl = end(hl_rows)["x"], end(hl_rows)["y"]
    sep = math.hypot(x_hl - x_ll, y_hl - y_ll)
    # the path-integrated separation (the robust gate — the final
    # positions alone can coincide while the paths diverge mid-run,
    # e.g. a fishtail that meets up at the end): the mean per-sample
    # |pos_ll - pos_hl| over the whole run (the sum normalized by the
    # duration — the same signal, comparable across scripts)
    n_path = min(len(ll_rows), len(hl_rows))
    path = (
        sum(
            math.hypot(
                ll_rows[i]["x"] - hl_rows[i]["x"], ll_rows[i]["y"] - hl_rows[i]["y"]
            )
            / NM
            for i in range(n_path)
        )
        / n_path
    )
    path_max = max(
        math.hypot(ll_rows[i]["x"] - hl_rows[i]["x"], ll_rows[i]["y"] - hl_rows[i]["y"])
        / NM
        for i in range(n_path)
    )

    w_ll = end(ll_rows)["crew"]["port"]["W_frac"]
    w_hl = end(hl_rows)["crew"]["port"]["W_frac"]

    def mean_rate(rows):
        return sum(r["crew"]["port"]["rate_eff"] for r in rows) / len(rows)

    rate_ll, rate_hl = mean_rate(ll_rows), mean_rate(hl_rows)

    d_turn = {}
    for name, rows in (("ll", ll_rows), ("hl", hl_rows)):
        t_c, y_c = _interp_cross(rows, "psi", math.pi, out_key="y")
        if t_c is not None:
            d_turn[name] = abs(y_c)
    d_diff = None
    if "ll" in d_turn and "hl" in d_turn:
        d_diff = d_turn["hl"] / d_turn["ll"] - 1.0

    # accumulated fatigue: the total W' consumed (the sum of the negative
    # W_frac steps — the endpoint W_frac alone is a brittle boundary state)
    def depletion(rows):
        w = [r["crew"]["port"]["W_frac"] for r in rows]
        return sum(max(0.0, w[i] - w[i + 1]) for i in range(len(w) - 1))

    dep_ll, dep_hl = depletion(ll_rows), depletion(hl_rows)

    # per-bin trajectory residuals (task T5, VALIDATION §11): 3-min
    # mean-speed bins, the max |bin| diff and the RMS, in % of the LL
    # bin mean. The caller passes the scoped bins (the cruise_turn
    # back-tail window — the HL's documented domain boundary, §9.3.5)
    # to exclude.
    def bin_diffs(rows_ll, rows_hl, bw=180.0, exclude=()):
        def binned(rows):
            out = []
            for r in rows:
                b = int(r["t"] // bw)
                while len(out) <= b:
                    out.append([])
                out[b].append(r["V"])
            return [sum(b) / len(b) for b in out]

        bl, bh = binned(rows_ll), binned(rows_hl)
        diffs = []
        for i, (a, b) in enumerate(zip(bl, bh)):
            if i in exclude or a <= 0.5 * KT:
                continue
            diffs.append((b / a - 1.0) * 100.0)
        if not diffs:
            return None, None
        mx = max(diffs, key=abs)
        rms = math.sqrt(sum(d * d for d in diffs) / len(diffs))
        return mx, rms

    return {
        "mean_speed": {"ll": ll_v / KT, "hl": hl_v / KT, "tol": 0.01, "unit": "kt"},
        "mean_speed_pct": {
            "ll": 0.0,
            "hl": ll_v and (hl_v / ll_v - 1.0),
            "tol": 0.01,
            "unit": "%",
        },
        "t_3nm": {"ll": t3.get("ll"), "hl": t3.get("hl"), "tol": 0.01, "unit": "s"},
        "t_3nm_pct": {
            "ll": 0.0,
            "hl": (t3["hl"] / t3["ll"] - 1.0) if "ll" in t3 and "hl" in t3 else None,
            "tol": 0.01,
            "unit": "%",
        },
        "turn_D": {
            "ll": d_turn.get("ll"),
            "hl": d_turn.get("hl"),
            "tol": 0.05,
            "unit": "m",
        },
        "turn_D_pct": {"ll": 0.0, "hl": d_diff, "tol": 0.05, "unit": "%"},
        "fatigue": {"ll": w_ll, "hl": w_hl, "tol": 0.05, "unit": "W_frac"},
        "fatigue_delta": {"ll": 0.0, "hl": w_hl - w_ll, "tol": 0.05, "unit": "pts"},
        "fatigue_consumed": {
            "ll": dep_ll,
            "hl": dep_hl,
            "tol": 0.05,
            "unit": "W' frac",
        },
        "fatigue_consumed_delta": {
            "ll": 0.0,
            "hl": dep_hl - dep_ll,
            "tol": 0.05,
            "unit": "pts",
        },
        "rate_eff": {"ll": rate_ll, "hl": rate_hl, "tol": 1.0, "unit": "spm"},
        "rate_eff_delta": {
            "ll": 0.0,
            "hl": rate_hl - rate_ll,
            "tol": 1.0,
            "unit": "spm",
        },
        "position_sep": {"ll": 0.0, "hl": sep / NM, "tol": 0.1, "unit": "NM"},
        "position_path": {"ll": 0.0, "hl": path, "tol": 0.1, "unit": "NM"},
        "position_max": {"ll": 0.0, "hl": path_max, "tol": 0.2, "unit": "NM"},
        "heading": {
            "ll": end(ll_rows)["psi"],
            "hl": end(hl_rows)["psi"],
            "tol": 5.0,
            "unit": "deg",
        },
        "distance": {
            "ll": d_ll[-1] / NM,
            "hl": d_hl[-1] / NM,
            "tol": 0.05,
            "unit": "NM",
        },
        "bin_max": {
            "ll": 0.0,
            "hl": bin_diffs(ll_rows, hl_rows, exclude=exclude_bins)[0],
            "tol": 5.0,
            "unit": "%",
        },
        "bin_rms": {
            "ll": 0.0,
            "hl": bin_diffs(ll_rows, hl_rows, exclude=exclude_bins)[1],
            "tol": 3.0,
            "unit": "%",
        },
    }


def equivalence_table(ll_rows, hl_rows, meta, title="") -> str:
    """The markdown equivalence table with verdicts + tolerance sources.
    The gates are the _pct / _delta / _sep rows; the raw-value rows
    (mean_speed, t_3nm, turn_D, fatigue, distance, heading) are
    informational — their tolerance is the paired gate row's."""
    m = metrics(ll_rows, hl_rows)
    cal = meta["calibration"]
    lines = [
        f"### {title}" if title else "### equivalence table",
        "",
        (
            f"calibration: {cal} · LL dt={meta['ll_dt']} s · "
            f"HL dt={meta['hl_dt']} s · 1 Hz samples · V0={meta['V0'] / KT:.1f} kt"
        ),
        "",
        "| metric | LL | HL | diff | tolerance | verdict |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for key, row in m.items():
        if row["hl"] is None:
            lines.append(f"| {key} | {row['ll']} | n/a | n/a | ±{row['tol']} | — |")
            continue
        ll, hl, tol = row["ll"], row["hl"], row["tol"]
        row["unit"]
        gated = key.endswith(("_pct", "_delta")) or key in (
            "position_sep",
            "position_path",
            "position_max",
        )
        if key.endswith("_pct") or key == "turn_D_pct":
            diff = f"{hl * 100:+.1f} %"
            ok = abs(hl) < tol
        elif key in (
            "fatigue_delta",
            "fatigue_consumed_delta",
            "position_sep",
            "position_path",
            "position_max",
        ):
            diff = f"{hl:+.3f}"
            ok = abs(hl) < tol
        else:
            diff = f"{hl - ll:+.3f}"
            ok = not gated or abs(hl - ll) < tol
        lines.append(
            f"| {key} | {ll:.3f} | {hl:.3f} | {diff} | {tol} | "
            f"{'—' if not gated else ('PASS' if ok else 'VIOLATION')} |"
        )
    return "\n".join(lines) + "\n"
