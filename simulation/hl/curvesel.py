"""The general curve-selection machinery (the LOOCV + AIC design).

Every fitted curve in the calibration is chosen by a principled recipe
instead of a hand grid: the candidate families are fitted by
CONTINUOUS least squares (no hand-chosen parameter steps), the AIC
picks the family — the LL is a deterministic oracle, so the AIC's
penalty is pure parsimony (the family's expressiveness, not sampling
noise) — and the window LOOCV reports the parameters' stability across
the fit-window lengths (the fragility the hand-chosen windows had).
The acceptance gates stay the final arbiter: the yaw-build's selection
is checked on the HL's response (the sprint/zig-zag position rows)
before it is accepted, exactly as the tau_exit scan is.

The static tables (the d_oar_v drained curve) are fitted as fractional
polynomials: d(V) = a + b·V^p1 + c·V^p2 (the standard power set; the
repeated power uses the V^p·ln V form), the degree and powers chosen
by the AIC.
"""

import math
from typing import Any

import numpy as np
from scipy.optimize import least_squares

# The yaw-build's nested families: single-tau rise, delayed single-tau
# (the yaw inertia's flat start), two-timescale (the fast share A at
# tf, then the sway-coupled tail at ts), delayed two-timescale.
YAW_FAMILIES = ("single", "dsingle", "two", "dtwo")

# The standard fractional-polynomial power set.
FP_POWERS = (-2.0, -1.0, -0.5, 0.5, 1.0, 2.0, 3.0)


# -- the yaw-build families -------------------------------------------


def yb_shape(t, family, x):
    """The family's shape with the settle factored out: f(t), 0..1."""
    if family == "single":
        (tau,) = x
        return 1.0 - np.exp(-t / tau)
    if family == "dsingle":
        td, tau = x
        return np.where(t < td, 0.0, 1.0 - np.exp(-(t - td) / tau))
    if family == "two":
        A, tf, ts = x
        return 1.0 - A * np.exp(-t / tf) - (1.0 - A) * np.exp(-t / ts)
    A, tf, ts, td = x
    return np.where(
        t < td,
        0.0,
        1.0 - A * np.exp(-(t - td) / tf) - (1.0 - A) * np.exp(-(t - td) / ts),
    )


def yb_bounds(family):
    """The shape params' bounds: the taus 0.5-120 s, the delay 0-6 s,
    the fast share A 0-1."""
    n = {"single": 1, "dsingle": 2, "two": 3, "dtwo": 4}[family]
    lo, hi = [], []
    for i in range(n):
        if family in ("two", "dtwo") and i == 0:
            lo.append(0.0)
            hi.append(1.0)  # A
        elif (family == "dsingle" and i == 1) or (family == "dtwo" and i == 3):
            lo.append(0.0)
            hi.append(6.0)  # td
        else:
            lo.append(0.5)
            hi.append(120.0)  # the taus
    return (lo, hi)


def yb_starts(family):
    """The multi-start points: the taus across the build's scales, the
    delays across the plausible inertia range."""
    starts = []
    for tau in (2.0, 5.0, 10.0, 20.0):
        if family == "single":
            starts.append((tau,))
        elif family == "dsingle":
            for td in (0.0, 1.0, 2.0):
                starts.append((td, tau))
        elif family == "two":
            for A in (0.5, 0.9):
                starts.append((A, tau, 15.0))
        else:
            for A in (0.5, 0.9):
                for td in (0.0, 1.0, 2.0):
                    starts.append((A, tau, 15.0, td))
    return starts


def fit_yaw_family(ts, ys, family, x0s):
    """The continuous least-squares fit of one family with the settle
    PROFILED out: the optimal ss for any shape is the closed-form
    ss = sum(y·f)/sum(f^2), so the search is over the shape params
    only. Multi-start over x0s (the piecewise delay's local minima).
    Returns (rss, x) or None."""
    best = None
    for x0 in x0s:

        def resid(x):
            f = yb_shape(ts, family, x)
            ss = float(np.dot(ys, f) / np.dot(f, f))
            return ys - ss * f

        try:
            res = least_squares(
                resid, np.asarray(x0, float), bounds=yb_bounds(family), max_nfev=2000
            )
        except ValueError:
            continue
        rss = float(np.dot(res.fun, res.fun))
        if best is None or rss < best[0]:
            best = (rss, res.x)
    return best


def yb_canonical(family, x, ss):
    """The family's fit mapped to the ship's (A, tf, ts, td) form."""
    if family == "single":
        (tau,) = x
        return {"A": 1.0, "tf": float(tau), "ts": float(tau), "td": 0.0, "ss": ss}
    if family == "dsingle":
        td, tau = x
        return {"A": 1.0, "tf": float(tau), "ts": float(tau), "td": float(td), "ss": ss}
    if family == "two":
        A, tf, ts = x
        return {"A": float(A), "tf": float(tf), "ts": float(ts), "td": 0.0, "ss": ss}
    A, tf, ts, td = x
    return {"A": float(A), "tf": float(tf), "ts": float(ts), "td": float(td), "ss": ss}


def select_yaw_family(rec, dt, label="", force=None):
    """The yaw-build's family selection for one measurement record:
    fit all four nested families continuously, rank by the AIC
    (n·ln(RSS/n) + 2k — the deterministic oracle's parsimony), and
    report the window LOOCV: the summed leave-one-window-out error
    (the 30-s windows) and the parameter spread across the 30-120 s
    fit-window lengths (the hand-window fragility this replaces).
    force: a family name to return as the pick regardless of the AIC
    (the gate-arbiter's fallback). Returns the canonical
    (A, tf, ts, td) + the selection record."""
    ts = np.arange(1, len(rec) + 1) * dt
    ys = np.asarray(rec, float)
    rows: list[dict[str, Any]] = []
    for family in YAW_FAMILIES:
        hit = fit_yaw_family(ts, ys, family, yb_starts(family))
        if hit is None:
            continue
        rss, x = hit
        n = len(ys)
        k = len(x) + 1  # the shape params + the settle
        aic = n * math.log(max(rss / n, 1e-300)) + 2.0 * k
        f = yb_shape(ts, family, x)
        ss = float(np.dot(ys, f) / np.dot(f, f))
        w = 30.0 / dt
        nw = max(1, int(len(ys) // w))
        loo = 0.0
        for iw in range(nw):
            keep = np.ones(len(ys), bool)
            keep[int(iw * w) : int((iw + 1) * w)] = False
            if keep.sum() < 20:
                continue
            h2 = fit_yaw_family(ts[keep], ys[keep], family, [x])
            if h2 is None:
                continue
            _, x2 = h2
            f2 = yb_shape(ts[~keep], family, x2)
            ss2 = float(np.dot(ys[~keep], f2) / np.dot(f2, f2))
            loo += float(np.sum((ys[~keep] - ss2 * f2) ** 2))
        spans = {}
        for T in (30.0, 45.0, 60.0, 90.0, 120.0):
            m = min(len(ys), int(T / dt))
            h3 = fit_yaw_family(ts[:m], ys[:m], family, [x])
            if h3 is not None:
                spans[T] = h3[1]
        can = yb_canonical(family, x, ss)
        rows.append(
            {
                "family": family,
                "rss": rss,
                "aic": aic,
                "ss": ss,
                "x": list(x),
                "loo": loo,
                "spans": spans,
                "canon": can,
            }
        )
    rows.sort(key=lambda r: float(r["aic"]))
    if not rows:
        raise RuntimeError(f"no yaw family fitted for {label}")
    pick = (
        next((r for r in rows if r["family"] == force), rows[0]) if force else rows[0]
    )
    pick_x: list[Any] = pick["x"]
    pick_spans: dict[float, Any] = pick["spans"]
    names = ("A", "tf", "ts", "td")[: len(pick_x)]
    spread = {}
    for i, name in enumerate(names):
        vals = [s[i] for s in pick_spans.values()]
        spread[name] = (max(vals) - min(vals)) if vals else float("nan")
    can = yb_canonical(pick["family"], pick["x"], pick["ss"])
    return dict(
        family=pick["family"],
        ranking=[
            {
                "family": r["family"],
                "aic": r["aic"],
                "rss": r["rss"],
                "loo": r["loo"],
                "canon": r["canon"],
            }
            for r in rows
        ],
        win_spread=spread,
        **can,
    )


# -- the fractional polynomials (the static tables) --------------------


def fp_design(v, p1, p2):
    """The FP2 design matrix: [1, V^p1, V^p2]; the repeated power
    p1 == p2 uses the V^p·ln V form (the standard convention)."""

    def col(p):
        if p == 0.0:
            return np.log(v)
        c = np.power(v, p)
        return c

    c1 = col(p1)
    if p1 == p2:
        c2 = c1 * np.log(v)
    else:
        c2 = col(p2)
    return np.column_stack([np.ones_like(v), c1, c2])


def fit_fp(vs, ds):
    """The fractional-polynomial selection for a 1-D static table:
    fit FP1 (the single power) and FP2 (the power pair) over the
    standard power set by least squares (the linear-in-parameters
    closed form), choose by the AIC, and report the leave-one-point-
    out error. Returns (powers, coeffs, record)."""
    v = np.asarray(vs, float)
    y = np.asarray(ds, float)
    n = len(y)
    best = None
    for deg, plist in ((1, FP_POWERS), (2, FP_POWERS)):
        for p1 in plist:
            if deg == 1:
                X = np.column_stack([np.ones_like(v), np.power(v, p1)])
                k = 2
            else:
                for p2 in plist:
                    X = fp_design(v, p1, p2)
                    k = 3
                    rss = _fp_rss(X, y)
                    loo = _fp_loo(v, y, p1, p2, deg)
                    aic = n * math.log(max(rss / n, 1e-300)) + 2.0 * k
                    rec = {
                        "deg": deg,
                        "p1": p1,
                        "p2": p2,
                        "rss": rss,
                        "aic": aic,
                        "loo": loo,
                    }
                    if best is None or aic < best["aic"]:
                        best = rec
                continue
            rss = _fp_rss(X, y)
            loo = _fp_loo(v, y, p1, p1, 1)
            aic = n * math.log(max(rss / n, 1e-300)) + 2.0 * k
            rec = {"deg": deg, "p1": p1, "p2": p1, "rss": rss, "aic": aic, "loo": loo}
            if best is None or aic < best["aic"]:
                best = rec
    if best is None:
        raise RuntimeError("no fractional polynomial fitted")
    p1, p2 = best["p1"], best["p2"]
    X = (
        fp_design(v, p1, p2)
        if best["deg"] == 2
        else np.column_stack([np.ones_like(v), np.power(v, p1)])
    )
    coeffs = np.linalg.lstsq(X, y, rcond=None)[0]
    best["coeffs"] = list(coeffs)
    return best


def _fp_rss(X, y):
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    r = y - X @ b
    return float(np.dot(r, r))


def _fp_loo(v, y, p1, p2, deg):
    """The leave-one-point-out sum of squared errors."""
    tot = 0.0
    n = len(y)
    for i in range(n):
        keep = np.ones(n, bool)
        keep[i] = False
        if deg == 1:
            X = np.column_stack([np.ones(keep.sum()), np.power(v[keep], p1)])
        else:
            X = fp_design(v[keep], p1, p2)
        b = np.linalg.lstsq(X, y[keep], rcond=None)[0]
        if deg == 1:
            Xt = np.array([1.0, v[i] ** p1])
        else:
            Xt = fp_design(np.array([v[i]]), p1, p2)[0]
        tot += (y[i] - float(np.dot(Xt, b))) ** 2
    return tot


def fp_eval(v, rec):
    """Evaluate the chosen fractional polynomial at v (a scalar or an
    array), in m for the d_oar_v's V in m/s."""
    v = np.asarray(v, float)
    if rec["deg"] == 1:
        X = np.column_stack([np.ones_like(v), np.power(v, rec["p1"])])
    else:
        X = fp_design(v, rec["p1"], rec["p2"])
    out = X @ np.asarray(rec["coeffs"], float)
    return float(out.item()) if np.ndim(v) == 0 else out
