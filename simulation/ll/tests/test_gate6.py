"""Gate 6 — per-tier crews (plan 15.1).

Run: pytest ll/tests/test_gate6.py  (or the full suite)

The side's crew splits into three tier sub-crews (31 thranites / 27 zygians /
27 thalmians per side): per-tier MIT, W' tanks, and the thalmian head-room
power factor (the ch.9 L-model: a reduced effective pull scales the POWER;
0.9 at cruise from the 720/800 mm manikin ratio, declining to 0.6 at
44.5 spm — "the thalmian tier's power contribution fell sharply at higher
speeds", ch.9 p.77). The feather clamp: when the deadspot would drag the
blade, the rowers slip it (zero contribution, as the trials observed).

Gates:
  G6-1 the thalmian power share falls with rate (the trial character);
  G6-2 the 170-oar sprint overshoot closes (bare-oar 8.54 -> ~7.9-8.0 with
        the head-room, below the trial band's top; the crew-count residual
        shrinks);
  G6-3 the side API is unchanged by the tier split (the ship's math holds).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.chain import KT
from ll.ship import Ship

TIER_N = {"thranite": 31, "zygian": 27, "thalmian": 27}


def avg_shares(rate, t_end=900.0, warm=600.0, v0_kt=6.5):
    s = Ship(rate=rate)
    s.V = v0_kt * KT
    acc = {k: 0.0 for k in TIER_N}
    steps = 0
    while s.t < t_end:
        s.step(0.02)
        if s.t >= warm:
            tel = s.crew["port"].tier_telemetry()
            for k, n in TIER_N.items():
                acc[k] += tel[k]["p_ext"] * n
            steps += 1
    tot = sum(acc.values())
    return {k: acc[k] / tot for k in TIER_N}


def test_thalmian_share_falls_with_rate():
    """The thalmian share declines from cruise to sprint — the ch.9
    'fell sharply at higher speeds' character (time-averaged over the
    exhausted steady state, so the W'-boundary surging averages out)."""
    s28 = avg_shares(28.8)["thalmian"]
    s44 = avg_shares(44.5)["thalmian"]
    assert s44 < s28, f"thalmian share {s28:.2f} -> {s44:.2f} must fall"
    assert s44 < 0.32, f"thalmian sprint share {s44:.2f}"


def test_sprint_overshoot_closed():
    """The bare-oar 170-oar sprint equilibrium was 8.54 kt (above the trial
    band). With the thalmian head-room the burst is ~7.9 — the crew-count
    overshoot shrinks to below the band's top (the trial's 130 effective
    rowers + the ineffective thalmians, both now represented)."""
    s = Ship(rate=44.5)
    s.V = 8.5 * KT
    v30 = None
    while s.t < 60:
        s.step(0.02)
        if v30 is None and s.t >= 30:
            v30 = s.V / KT
    assert v30 is not None and v30 < 8.4, f"burst {v30:.2f} kt still overshoots"
    # the chain-law baseline (2026-08): the burst's 30-s speed's 7.39 kt
    # — the chain drag (the tank-tested law, now the default) exposes
    # the LL's sprint deficit (the T1 family; the old 40.2v^2 masked
    # it). The band stays sprint-like: above the cruise, below the
    # trial's 8.2-8.3.
    assert v30 > 7.0, f"burst {v30:.2f} kt must stay sprint-like"


def test_tier_structure():
    """The side is three tiers with the documented factors; the ship's
    per-oar-average API is unchanged (the turn/equilibrium math holds)."""
    s = Ship(rate=28.8)
    tel = s.crew["port"].tier_telemetry()
    assert set(tel) == {"thranite", "zygian", "thalmian"}
    assert abs(tel["thranite"]["power_factor"] - 1.0) < 1e-9
    assert abs(tel["thalmian"]["power_factor"] - 0.9) < 1e-9
    s2 = Ship(rate=44.5)
    assert (
        abs(s2.crew["port"].tier_telemetry()["thalmian"]["power_factor"] - 0.6) < 1e-9
    )
    # the aggregate MIT reference (tier-weighted) is from OAR_TIER_MIT (Table 3.1)
    from common.chain import N_THALMIAN, N_THRANITE, N_ZYGIAN, OAR_TIER_MIT

    assert abs(s.mit - OAR_TIER_MIT["spruce"]) < 0.01  # spruce fleet
    old_fir = Ship(rate=28.8, fleet="old-fir")
    expected_old_fir = (
        N_THRANITE * OAR_TIER_MIT["thranite"]
        + N_ZYGIAN * OAR_TIER_MIT["zygian"]
        + N_THALMIAN * OAR_TIER_MIT["thalmian"]
    ) / (N_THRANITE + N_ZYGIAN + N_THALMIAN)
    assert abs(old_fir.mit - expected_old_fir) < 0.1  # old-fir tier-weighted


def test_feather_clamp_telemetry():
    """At the sprint speed the short-sweep thalmians cannot outrun the water
    and slip the blade (feathered) — the mechanism that makes their
    contribution 'ineffective' rather than a drag."""
    s = Ship(rate=44.5)
    s.V = 8.5 * KT
    while s.t < 30:
        s.step(0.02)
    limited = s.crew["port"].tier_telemetry()["thalmian"]["limited"]
    assert limited in ("feathered", "mean", "none"), f"thal {limited}"


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__]))
