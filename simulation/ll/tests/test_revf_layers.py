"""The Rev F A-basket (the realism upgrades): locks on the measured
behaviour of the labelled layers.

- A1: the per-station oar layer (ll/stations.py) — the yaw moment and
  the held-blade brake from the per-oar sums with the local (u, v, r)
  flow. The measured verdict: the effective lever 2.08 m (the geometric
  mean 1.36 + the local flow's 0.72 — the mechanism the fitted lever
  folds in, direction confirmed) but the turn D's shift out of the gate
  bands with the [?] station layout (tightest -25 %, the oar-only
  +15 %), so the aggregated sway-calibrated default stays (the negative
  result, next-steps.md A1).
- A2: the trapezoidal drive profile (ll/oar.py profile="trap") — the
  phase-based stroke with the report's in-water fraction. The measured
  verdict: with the same sweep the longer in-water forces a lower mean
  omega and the blade cannot outrun the water during the ramps (the
  mean thrust -35.5 N vs the chain's +17.5 N at 7.2 kt/28.8 spm); the
  effective-pull (the chain) and the kinematic in-water (the report)
  jointly imply a peaked mid-stroke omega the trapezoid cannot hold —
  the constant-omega stays (the negative result, next-steps.md A2).
"""

import math

import pytest

from common.chain import KT, RIGS
from ll.oar import Oar, simulate
from ll.ship import Ship, run_turn


def _one_turn(mode, rate, helm, state, v0_kt):
    s = Ship(rate=rate, helm=helm, oar_state=state,
             pressure=("spoude", "spoude"), stations=mode)
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
    expected = dict(g1=132.9, f1=261.2, tightest=57.6,
                    oar_hold=81.9, oar_back=78.4)
    for name, d in stations_turns.items():
        key = name.replace("-", "_")
        assert abs(d - expected[key]) < 3.0, f"{name}: {d:.1f}"


def test_stations_effective_lever():
    """A1: at the g1 settle the per-station sums give an effective
    lever ~4.6 m (the blade's mean arm 4.82 — the Taylor 4.8 confirmed
    as the BLADE arm, not the thole's) and a local-flow damping of
    ~400 kN m s. The fitted 1.8 is the NET (blade arm minus the
    damping), which the register C3 now records."""
    s = Ship(rate=28.8, helm=("port", 22.5 / 67.5), oar_state=("row", "row"),
             pressure=("spoude", "spoude"), stations=True)
    s.V = 6.5 * KT
    Q = Fd = om = 0.0
    n = 0
    while s.t < 500.0:
        s.step(0.01)
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
    assert 4.0 < lever < 5.2, f"effective lever {lever:.2f} m"  # the chain law: unchanged family
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


def test_drag_law_noop():
    """B4: the turn model's drag law is a measured no-op for the turn
    gates — the turns run below 6.7 kt where the taylor/trials laws
    agree on 40.2v^2, and the chain law shifts the D's by <= 1.1 % (the
    turn's drag is rudder-dominated). The t_360 is unchanged too."""
    from ll.ship import rate_for_speed
    rate = rate_for_speed("Olympias", 6.5, n_oars=85)
    ds = []
    for law in ("taylor", "trials", "chain"):
        s = Ship(rate=rate, n_oars=85, helm=("starboard", 1.0),
                 oar_state=("row", "hold"), pressure=("spoude", "spoude"),
                 drag_law=law)
        s.V = 6.5 * KT
        r = run_turn(s, dt=0.02, target_psi=math.pi)
        ds.append(r["D"])
    assert max(ds) - min(ds) < 1.5, ds


def test_mass_matrix_noop():
    """B1: the sway-yaw coupling matrix (the [?] semi-empirical added
    masses) shifts the g1 by < 3 % and the drift by < 0.3 deg — the
    couplings act on the transients, the drift is a steady-state
    balance; the trial-measured scalar m_app stays."""
    from ll.ship import rate_for_speed
    rate = rate_for_speed("Olympias", 6.0)
    ds = []
    for mm in (False, True):
        s = Ship(rate=rate, helm=("port", 1.0), oar_state=("row", "row"),
                 pressure=("spoude", "spoude"), mass_matrix=mm)
        s.V = 6.0 * KT
        r = run_turn(s, dt=0.02, target_psi=math.pi)
        ds.append(r["D"])
    assert abs(ds[1] - ds[0]) / ds[0] < 0.03, ds


def test_trap_profile_thrust():
    """A2: the trapezoidal drive with the report's in-water fraction at
    7.2 kt/28.8 spm — the measured NEGATIVE mean thrust (the negative
    result): the same sweep over a longer in-water time forces a lower
    mean omega; the blade cannot outrun the water during the ramps."""
    rig = RIGS["Olympias"]
    ref = simulate(Oar(rig, 28.8, 0.43), 7.2 * KT, 0.43 / 600, 6)
    trap = simulate(Oar(rig, 28.8, 0.39 * 60.0 / 28.8, profile="trap",
                        t_ramp=0.15), 7.2 * KT, 0.0005, 6)
    assert ref["mean_thrust"] > 10.0
    assert trap["mean_thrust"] < -20.0, trap["mean_thrust"]
