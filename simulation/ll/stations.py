"""The per-station oar layer (the Rev F comparison's A1 item).

The aggregated ship (ll/ship.py) turns through the fitted oar-race
lever (1.8 m, sway-calibrated — the register C3 decomposition of
Taylor's 4.8). This layer places the 170 oars at their stations and
lets the yaw moment and the held-blade brake emerge from the per-oar
sums, with each blade's flow computed from the ship's (u, v, r) at its
station — the mechanism the lever's lateral dynamics fold in.

Layout (the register B6 station-plan gap; flagged assumptions):

  - per side: thranite 31 / zygian 27 / thalmian 27 stations, evenly
    spaced at the chain's interscalmium 0.888 m, centred on the oar
    race [?] (the even-spacing assumption — the station plan's drawing
    (Rev F Figure 16) is not yet decoded);
  - the zygian/thalmian banks occupy the middle 27 stations; their
    extreme stations (the bow/stern) carry the SHORT oars (Rev F Table
    3: 4.0 m overall, the inboard/outboard scaled by the table's
    ratios, 2 stations per side [?]);
  - the athwartships arms: thranite 1.8 / zygian 1.4 / thalmian 1.0 m
    [?] (the outrigger geometry's estimate — the physical mean the
    sway-calibration's 1.8 sits above, the gap being the local-flow
    moment this layer computes).

The local blade flow (the report's model): the blade's velocity
relative to the water includes the ship's rotation and sway at the
blade's position: vn = (u - r·y)·nx + (v + r·x)·ny - l_cp·|omega|,
with (x, y) the station's position (the blade's own sweep's tangential
speed inside the l_cp·omega term). Port and starboard oars mirror
(C_star = -C_port), so their lateral forces oppose, as physically.

The layer is swappable (Ship(..., stations=True)); the aggregated
validated default stays. The acceptance (next-steps.md A1): the
one-side-stops gates hold with the per-station sums, and the drift
moves toward the trials' 8-15°.
"""

import math

INT = 0.888            # m — interscalmium (the chain)
# the thole athwartships arms — PHYSICAL geometry, bounded by the
# sources (not tuning coefficients; the per-station layer's whole
# point is that the fitted lever disappears):
#   thranite 2.7 m  — the outrigger's centre: the register B6 beam
#                    5.45-5.6 m, the tholes drilled through the upper
#                    + lower outrigger rails (build log, rig-geometry
#                    §2) — GROUNDED
#   zygian   ~2.0 m — between the top timbers, lining up with the
#                    outrigger brackets [?] (the B6 decode would pin it)
#   thalmian ~1.2 m — "far inboard" (to keep the lower oar angle
#                    shallow — the build log's own words) [?]
ARM = {"thranite": 2.7, "zygian": 2.0, "thalmian": 1.2}   # m
# the short oars (Rev F Table 3): overall 4.0 vs 4.22; the inboard to
# the handle centre 0.774 vs 0.935, the outboard to the blade centre
# 2.781 vs 2.873 — the chain's rig scaled by those ratios
SHORT = dict(lin_scale=0.774 / 0.935, lout_scale=2.781 / 2.873)
SHORT_STATIONS = 2     # per side at each end [?]

N_TIER = {"thranite": 31, "zygian": 27, "thalmian": 27}   # per side


def station_layout():
    """The per-side stations: {tier: [(x, y, short), ...]} — x fore-aft
    (m, + bow), y athwartships (+ port), short = the short-oar flag."""
    out = {}
    xs = [(i - 15) * INT for i in range(31)]       # 31 evenly spaced [?]
    for tier in ("thranite", "zygian", "thalmian"):
        n = N_TIER[tier]
        lo = (31 - n) // 2                          # the middle 27
        st = []
        for i in range(lo, lo + n):
            short = tier in ("zygian", "thalmian") \
                and (i - lo < SHORT_STATIONS or lo + n - 1 - i < SHORT_STATIONS)
            st.append((xs[i], ARM[tier], short))
        out[tier] = st
    return out


def short_rig(rig: dict) -> dict:
    """The short oar's rig: the chain's geometry scaled by the Rev F
    Table 3 ratios (the short zygian/thalmian, 4.0 m overall)."""
    r = dict(rig)
    r["lin"] = rig["lin"] * SHORT["lin_scale"]
    r["lout"] = rig["lout"] * SHORT["lout_scale"]
    return r


def local_vn(flow, nx, ny, l_cp, omega):
    """The blade's normal flow with the ship's rotation and sway at the
    station: vn = (u - r·y)·nx + (v + r·x)·ny + l_cp·omega (the oar's
    own sweep inside the omega term — the same form as the base law)."""
    u, v, r, x, y = flow
    return (u - r * y) * nx + (v + r * x) * ny + l_cp * omega


def blade_pos(x_t, y_t, side, lout, C_eff):
    """The blade centroid's position in ship axes at the side-local oar
    angle C_eff (rad from athwartships, + toward the bow): the yaw
    moment's arm is the BLADE's position, not the thole's — the oar and
    the rower are internal to the hull's rigid body (the report's own
    note), so the net moment is r_blade x F. The blade's reach:
    x_b = x_t + lout·sin(C_eff), y_b = y_t + lout·cos(C_eff)."""
    return x_t + lout * math.sin(C_eff), y_t + lout * math.cos(C_eff)
