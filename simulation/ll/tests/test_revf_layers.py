"""The Rev F A-basket (the realism upgrades): locks on the measured
behaviour of the labelled layers.

- A1: the per-station oar layer (ll/stations.py) — the yaw moment and
  the held-blade brake from the per-oar sums with the local (u, v, r)
  flow. The measured verdict: the effective lever 2.08 m (the geometric
  mean 1.36 + the local flow's 0.72 — the mechanism the fitted lever
  folds in, direction confirmed) but the turn D's shift out of the gate
  bands with the [?] station layout (tightest -25 %, the oar-only
  +15 %), so the aggregated sway-calibrated default stays (the negative
  result, next-steps.md Stream B2).
"""

import math

import pytest
from common.chain import KT, RIGS
from ll.oar import Oar, simulate
from ll.ship import Ship, run_turn


def _one_turn(mode, rate, helm, state, v0_kt):
    # the per-station layer is the KINEMATIC layer (its contract — the
    # force mode's per-oar EOM is not phase-locked and keeps the scalar
    # loop) — the layer's tests stay kinematic explicitly
    s = Ship(
        rate=rate,
        helm=helm,
        oar_state=state,
        pressure=("spoude", "spoude"),
        stations=mode,
        force=False,
    )
    s.V = v0_kt * KT
    r = run_turn(s, dt=0.02, target_psi=math.pi)
    return r["D"]


@pytest.fixture(scope="module")
def stations_turns():
    """The five harness turn cells in the stations mode (the A1
    measurement): V0 6.0/6.5 kt, the rate from rate_for_speed, helm
    full/22.5, 170/85 oars — the harness's own cells."""
    from ll.ship import rate_for_speed

    cells = [
        ("g1", 6.0, 170, ("port", 1.0), ("row", "row")),
        ("f1", 6.0, 170, ("port", 22.5 / 67.5), ("row", "row")),
        ("tightest", 6.5, 85, ("starboard", 1.0), ("row", "hold")),
        ("oar-hold", 6.5, 85, ("midship", 0.0), ("row", "hold")),
        ("oar-back", 6.5, 85, ("midship", 0.0), ("row", "back")),
    ]
    out = {}
    for name, v0, n, helm, state in cells:
        rate = rate_for_speed("Olympias", v0, n_oars=n)
        out[name] = _one_turn(True, rate, helm, state, v0)
    return out


def test_stations_turn_diameters(stations_turns):
    """A1: the stations-mode D's (the blade-arm moments + the local
    flow, the [?] layout) — locked so the layer's behaviour is known;
    the gates' comparison is the verdict (the aggregated default
    stays). The pattern is INVERTED vs the trials (the g1's 2.6x wider
    while the oar turns' 23% tighter) — the layer's net turn pattern
    does not match reality yet (the over-damping, next-steps A1)."""
    # Grounded hull (Stream C B1/B3, real offsets, LWL 32.35 m, trial WL
    # 1.10 m, mass 40.95 t / Iz 4.76e6): Ywl 1.845->A_lat 30.09, J 23217,
    # Omega 3.00e6, clr 0.93. Stations layer re-measured (kinematic,
    # force=False): g1 134.5, f1 264.4, tightest 57.9, oar_hold 83.0,
    # oar_back 77.1 — still inverted vs trials, aggregated default stays
    # (B3 shift +1.0/-0.7/+0.6/+0.8/+0.5 m vs fitted mass).
    expected = {
        "g1": 134.5,
        "f1": 264.4,
        "tightest": 57.9,
        "oar_hold": 83.0,
        "oar_back": 77.1,
    }
    for name, d in stations_turns.items():
        key = name.replace("-", "_")
        assert abs(d - expected[key]) < 3.0, f"{name}: {d:.1f}"


def test_stations_effective_lever():
    """A1: at the g1 settle the per-station sums give an effective
    lever ~4.6 m (the blade's mean arm 4.82 — the Taylor 4.8 confirmed
    as the BLADE arm, not the thole's) and a local-flow damping of
    ~400 kN m s. The fitted 1.8 is the NET (blade arm minus the
    damping), which the register C3 now records."""
    s = Ship(
        rate=28.8,
        helm=("port", 22.5 / 67.5),
        oar_state=("row", "row"),
        pressure=("spoude", "spoude"),
        stations=True,
        force=False,
    )
    s.V = 6.5 * KT
    Q = Fd = om = 0.0
    n = 0
    while s.t < 500.0:
        s.step(0.02)
        if s.t > 400.0:
            for crew in s.crew.values():
                for fxi, fyi, bri, x_b, y_b in crew._stations:
                    Q += x_b * fyi - y_b * fxi - y_b * bri
                    Fd += math.copysign(fxi, y_b)
            om += s.omega
            n += 1
    Q, Fd, om = Q / n, Fd / n, om / n
    lever = abs(Q / Fd)
    damp = abs(Q) / abs(om) / 1000.0
    assert 4.0 < lever < 5.2, (
        f"effective lever {lever:.2f} m"
    )  # the chain law: unchanged family
    assert 300 < damp < 500, f"damping {damp:.0f} kN m s"


def test_polar_variant_thrust():
    """B2: the macon-polars variant (C_L = sin 2a, C_D = 2 sin^2 a —
    the normal-component form) gives +40 % mean thrust at 7.2 kt/28.8
    — the lift is NOT negligible at the trireme's 54-58 deg angles of
    attack; the chain's calibrated C_N·A absorbs the shortfall (the A5
    register). The variant's OFF by default."""
    import ll.blade

    rig = RIGS["Olympias"]
    ref = simulate(Oar(rig, 28.8, 0.43), 7.2 * KT, 0.43 / 600, 6)
    ll.blade.BLADE_POLAR = True
    try:
        pol = simulate(Oar(rig, 28.8, 0.43), 7.2 * KT, 0.43 / 600, 6)
    finally:
        ll.blade.BLADE_POLAR = False
    assert 1.25 < pol["mean_thrust"] / ref["mean_thrust"] < 1.55
