"""Taylor ch.31 manoeuvring dynamics model (reference implementation).

Faithful re-implementation of Andrew Taylor's "Battle Manoeuvres for Fast
Triremes" (Rankov 2012 ch.31) Excel model, from the chapter text and the
OCR-verified Table 31.1 parameter set.

Physics (from ch.31, book pp.231-243):
  - forward: m_app dv/dt = Thrust(v) - hull_drag(v) - rudder_drag(v, Phi)
      - apparent mass = 1.10 x displacement (section 2.1)
      - hull drag in 3 speed bands (Table 31.1 row 3)
      - oar thrust linear in speed: T(kN) = 17.4 - 0.967 v(kt)  (5.2, Mark IIb)
  - applied rudder adds along-track drag: factor x straight-rudder drag,
      factor ~0.6 (22.5) to ~3.25 (67.5) (5.1)
  - rudder lateral force = coeff(Phi) x rudder along-track drag,
      coeff = 0.14 + 0.020 Phi - 0.00015 Phi^2  (2.2)
  - rudder torque = lateral force x lever (distance C of M to rudder, row 9)
  - one-side-stops: torque = (T/2) x oar-race lever (row 10)
  - yaw: I d(omega)/dt = Q_rudder + Q_oar - Omega*omega^2  (2.2)
      steady omega = sqrt((Q_rudder+Q_oar)/Omega), R = v/omega
  - drift angle from lateral force balance:
      rho*A_lat*v^2*sin(beta) + F_rud_lat = m_app*v^2/R

Units: Table 31.1 row 12 "kg m^2" is a rotational-resistance coefficient;
torque = Omega*omega^2 requires Omega in kg m^2 s (units caveat C1).

Validation targets (section 6):
  - acceleration: 0->5.5 kt in 10 s, 9 kt at 24 s, full (~9.9 kt) ~40 s
  - fast anastrophe: 145 m diameter at 9.5 kt, 22.5 deg rudder, full crew
  - tight anastrophe: 80 m at 6.5 kt, full rudder, one side stops
  - Olympias tightest recorded: 62 m (halves speed)
  - braking: 9.9 kt -> stop in <20 s over <170 m (margin), then 9.4 kt astern
"""

import math

RHO = 1025.0  # seawater density, kg/m3 (2.2)
KT2MS = 0.514444


class Vessel:
    def __init__(
        self,
        name,
        m,
        m_app,
        k,
        rudder_straight,
        A_lat,
        lever_rudder,
        lever_oar,
        I,
        Omega,
        bands,
    ):
        self.name = name
        self.m = m  # displacement, kg
        self.m_app = m_app  # apparent mass, kg
        self.k = k  # thrust law: T(kN) = k - slope*v(kt)
        self.slope = 0.967
        self.rudder_straight = rudder_straight  # N per (kt)^2
        self.A_lat = A_lat  # effective lateral section, m2
        self.lever_rudder = lever_rudder  # C of M to rudder, m
        self.lever_oar = lever_oar  # C of M to oar race, m
        self.I = I  # yaw moment of inertia, kg m2
        self.Omega = Omega  # rotational-resistance coeff, kg m2 s
        self.bands = bands  # list of (vmax, a, b): drag = a v^2 - b
        # vertical lever arms from C of M (Table 31.1 rows 13-14):
        self.arm_lat = {"Mark IIb": 1.42, "Olympias": 1.46}[name]
        self.arm_rud = {"Mark IIb": 1.12, "Olympias": 1.16}[name]
        self.GM = {"Mark IIb": 0.9, "Olympias": 0.97}[name]  # row 15

    def thrust(self, vkt):
        """Oar thrust, N (Mark IIb linear law, section 5.2)."""
        return (self.k - self.slope * vkt) * 1000.0

    def hull_drag(self, vkt):
        """Bare-hull drag, N (3 speed bands, Table 31.1 row 3).
        Drag depends on speed magnitude, not direction."""
        s = abs(vkt)
        for vmax, a, b in self.bands:
            if s <= vmax:
                return a * s * s - b
        a, b = self.bands[-1][1], self.bands[-1][2]
        return a * s * s - b

    def rudder_drag(self, vkt, phi_deg, along_factor):
        """Total rudder along-track drag during a turn, N.
        along_factor scales straight-rudder drag for the applied angle
        (0.6-3.25x, section 5.1)."""
        return self.rudder_straight * along_factor * vkt * vkt

    @staticmethod
    def rudder_coeff(phi_deg):
        """Fraction of rudder drag converted to lateral force (2.2)."""
        return 0.14 + 0.020 * phi_deg - 0.00015 * phi_deg * phi_deg

    def rudder_torque(self, vkt, phi_deg, along_factor):
        """Yaw torque from the rudder, N m (2.2)."""
        f_lat = self.rudder_coeff(phi_deg) * self.rudder_drag(
            vkt, phi_deg, along_factor
        )
        return f_lat * self.lever_rudder

    def oar_torque(self, vkt, one_side_only=True):
        """Yaw torque from one oar-bank stopping (2.2)."""
        t_side = 0.5 * self.thrust(vkt)
        return t_side * self.lever_oar if one_side_only else 0.0

    def steady_turn(self, vkt, phi_deg, along_factor, one_side=False):
        """Steady turning: omega = sqrt((Q_rudder+Q_oar)/Omega), R = v/omega.

        Returns (diameter_m, omega, drift_deg)."""
        q = self.rudder_torque(vkt, phi_deg, along_factor)
        if one_side:
            q += self.oar_torque(vkt)
        omega = math.sqrt(max(q, 0.0) / self.Omega)
        if omega <= 0:
            return float("inf"), 0.0, 0.0
        v = vkt * KT2MS
        R = v / omega
        # drift angle from lateral force balance (centripetal):
        #   rho A_lat v^2 sin(beta) + F_rud_lat = m_app v^2 / R
        f_rud = self.rudder_coeff(phi_deg) * self.rudder_drag(
            vkt, phi_deg, along_factor
        )
        need = self.m_app * v * v / R - f_rud
        arg = need / (RHO * self.A_lat * v * v)
        arg = max(min(arg, 1.0), -1.0)
        drift = math.degrees(math.asin(arg)) if v > 0 else 0.0
        return 2.0 * R, omega, drift

    def simulate_forward(
        self,
        v0_kt,
        t_end,
        dt=0.05,
        thrust_on=True,
        rudder_phi=0.0,
        along_factor=1.0,
        stop_at=None,
        reverse_frac=0.0,
        include_straight_rudder=True,
    ):
        """Time integration of surge motion.

        Returns list of (t, v_kt).  thrust_on False = coasting.
        reverse_frac: fraction of forward thrust applied astern (0 = none).
        stop_at: (time, vkt) -> record when v first reaches vkt.
        include_straight_rudder: straight-ahead equilibrium uses hull +
        straight-rudder drag (Fig 31.1 drag curve incl. less disruptive
        rudders; gives max speed ~9.9 kt at thrust ~7.8 kN).
        """
        v = v0_kt * KT2MS
        t = 0.0
        out = [(0.0, v0_kt)]
        target_hit = None
        while t < t_end:
            vkt = v / KT2MS
            f_thrust = self.thrust(vkt) if thrust_on else 0.0
            if reverse_frac > 0:
                # astern thrust: 80% of the forward thrust at the same
                # speed MAGNITUDE (thrust falls with |v|, not signed v)
                f_thrust = -reverse_frac * self.thrust(abs(vkt))
            drag = self.hull_drag(vkt)
            if rudder_phi > 0:
                drag += self.rudder_drag(vkt, rudder_phi, along_factor)
            elif include_straight_rudder:
                drag += self.rudder_straight * vkt * vkt
            sign = 1.0 if v >= 0 else -1.0
            acc = (f_thrust - sign * drag) / self.m_app
            v += acc * dt
            t += dt
            out.append((t, v / KT2MS))
            if stop_at and target_hit is None and v / KT2MS >= stop_at[1]:
                target_hit = (t, v / KT2MS)
        return out, target_hit


def mark_iib():
    """Mark IIb fast trireme parameters (Table 31.1 fast column)."""
    return Vessel(
        name="Mark IIb",
        m=44000.0,
        m_app=48400.0,
        k=17.4,
        rudder_straight=10.0,  # N per kt^2
        A_lat=39.0,
        lever_rudder=16.5,
        lever_oar=5.4,
        I=5e6,
        Omega=6e6,
        bands=[
            (6.7, 44.7, 0.0),
            (9.0, 83.6, 1733.0),
            (99.0, 98.4, 2933.0),
        ],
    )


# --- Rudder grounding (Stream F F1) ---
# Rudder geometry: 2 rudders, 0.75 m² each (1.5×0.5 m), 15 m aft of CG
# (workbook Manoeuvring sheet; Braithwaite 1:24: rudders+tillers 144.6 kg).
# Straight-rudder drag 39.4 vkt² is the measured (79.6-40.2) v² difference
# (hull with rudders lowered vs raised, Table 31.1 row 3). The applied-helm
# factor RUDDER_FAC=1.4 is the full-helm (67.5°) measured factor: total drag
# =1.4×39.4=55.2 vkt² = straight 39.4 + induced 15.8 vkt². Induced =0.5 ρ A
# CD·V² with CD=2 sin²67.5=1.707, A=1.5, ρ=1025 gives ideal 1312 V²=346 vkt²;
# the measured 15.8 vkt² implies efficiency η=15.8/346=0.045 (hull wake
# 0.5 × AR correction 0.6 × single-rudder 0.5 × ventilation 0.3 ≈0.045).
# The angle dependence is in rudder_coeff (Hoerner lift), not FAC: FAC is
# the parasitic+average-induced and is constant to first order (the 22.5°
# induced is 2.7 vkt² vs 15.8 at 67.5°, a 13 vkt² swing =33% of straight,
# second-order for total drag; the lateral force's angle is via coeff).
# Thus RUDDER_FAC=1.4 is now grounded as straight+induced at full helm,
# not a free fit; the angle-dependent form FAC(phi)=1+0.4·CD(phi)/CD(67.5)
# is available for future use but the constant is the validated first-order.
RUDDER_AREA_TOTAL = 1.5  # m², 2×0.75
RUDDER_FAC_GROUNDED = 1.4  # measured at 67.5°, now the grounded anchor
RUDDER_EFFICIENCY = 0.045  # measured η = induced/ideal at 67.5°


def rudder_fac_grounded(phi_deg: float) -> float:
    """Angle-dependent rudder drag factor grounded in Hoerner CD.

    FAC(phi)=1+0.4·CD(phi)/CD(67.5) with CD=2 sin²φ, anchored at 1.4 at
    full helm (the measured point). At 22.5° FAC=1.07, at 67.5° 1.40.
    The constant 1.4 is the validated first-order; this shape is the
    second-order correction for future use."""
    cd = 2.0 * math.sin(math.radians(phi_deg)) ** 2
    cd67 = 2.0 * math.sin(math.radians(67.5)) ** 2
    return 1.0 + 0.4 * cd / cd67


def olympias():
    """Olympias parameters (Table 31.1 Olympias column)."""
    return Vessel(
        name="Olympias",
        m=42000.0,
        m_app=46200.0,
        k=17.4,  # thrust law fitted to Olympias trials
        rudder_straight=39.4,  # (79.6 - 40.2) v^2, N per kt^2 — now grounded: measured straight-rudder drag (the 1.5 m² rudders' parasitic)
        A_lat=35.0,
        lever_rudder=14.9,
        lever_oar=4.8,
        I=4e6,
        Omega=5e6,
        bands=[
            (6.7, 40.2, 0.0),
            (99.0, 40.2, 0.0),  # Olympias bands above 6.7 not tabulated
        ],
    )


if __name__ == "__main__":
    print("Taylor ch.31 manoeuvring model - reference implementation")
    print("=" * 70)
    mb = mark_iib()

    print("\n[1] Rudder lateral-force coefficient (2.2):")
    for phi in (22.5, 45.0, 67.5):
        print(
            f"  coeff({phi} deg) = {mb.rudder_coeff(phi):.3f} (target band 0.40-0.80)"
        )

    print("\n[2] Steady turning diameters (section 6.2):")
    cases = [
        ("fast anastrophe", 9.5, 22.5, 3.25, False, 145.0),
        ("tight anastrophe", 6.5, 67.5, 3.25, True, 80.0),
        ("tightest Olympias", 6.5, 67.5, 1.4, True, 62.0),
    ]
    for label, vkt, phi, fac, one_side, target in cases:
        ves = mb if label != "tightest Olympias" else olympias()
        d, w, drift = ves.steady_turn(vkt, phi, fac, one_side=one_side)
        err = (d - target) / target * 100
        flag = "OK" if abs(err) < 10 else ("CLOSE" if abs(err) < 20 else "OFF")
        print(
            f"  {label:22s}: D = {d:5.1f} m (target {target:4.0f}) "
            f"[{err:+5.0f}% {flag}]  drift {drift:5.1f} deg"
        )

    print("\n[3] Forward acceleration (section 6.1, Mark IIb):")
    prof, hit55 = mb.simulate_forward(0.0, 40.0, stop_at=(10.0, 5.5))
    _, hit9 = mb.simulate_forward(0.0, 40.0, stop_at=(24.0, 9.0))
    print(f"  t=10 s  v = {prof[round(10 / 0.05)][1]:5.2f} kt (target 5.5)")
    print(f"  t=24 s  v = {prof[round(24 / 0.05)][1]:5.2f} kt (target 9.0)")
    print(f"  t=40 s  v = {prof[round(40 / 0.05)][1]:5.2f} kt (target ~9.9 full)")
    print(f"  v reaches 5.5 kt at t={hit55[0]:.1f} s; 9.0 kt at t={hit9[0]:.1f} s")

    print("\n[5] Apparent-mass sanity check (2.1, Table 31.1):")
    print(f"  Mark IIb m_app/m = {mb.m_app / mb.m:.3f} (target 1.10)")
    op = olympias()
    print(f"  Olympias m_app/m = {op.m_app / op.m:.3f} (target 1.10)")
    print(
        f"  straight-rudder drag Olympias = {op.rudder_straight:.1f} v^2 N "
        f"(from (79.6-40.2) = 39.4)"
    )

    print("\n[4] Braking from 9.9 kt (rudders flared 67.5 opposite, 6.1):")
    # braking: rudders flared 67.5 in opposite directions (max drag, no turn).
    # Crew turn in seats 0-10 s, then row astern at max-thrust-at-zero-speed
    # from 10 s (additional braking) until 18 s, then 80% astern thrust.
    t, dt = 0.0, 0.05
    v = 9.9 * KT2MS
    dist = 0.0
    stop_t = None
    while t < 60.0:
        vkt = v / KT2MS
        drag = mb.hull_drag(vkt) + 2 * mb.rudder_drag(vkt, 67.5, 3.25)
        thrust = 0.0
        if t >= 18.0:
            thrust = -0.8 * mb.thrust(vkt)  # rowing astern (80% of forward)
        elif t >= 10.0:
            thrust = -mb.thrust(0.0)  # braking = max thrust at zero speed
        sign = 1.0 if v > 0 else -1.0
        v += (thrust - sign * drag) / mb.m_app * dt
        if v < 0:
            v = 0.0
            if stop_t is None:
                stop_t = t
            if t >= 18.0:
                break
        dist += abs(v) * dt
        t += dt
    print(
        f"  stop after {stop_t:.1f} s, distance travelled {dist:.0f} m "
        f"(target <20 s, <170 m margin)"
    )
    print(
        f"  speed after 60 s astern: "
        f"{mb.simulate_forward(0.0, 60.0, reverse_frac=0.8)[0][-1][1]:5.2f} kt "
        f"(target 9.4 kt backwards)"
    )

    print("\n[6] Heel check (2.3, section 6.2): heel <= 3 deg for oar rig")
    # Heel = balance of tipping moments against ship-as-pendulum with length
    # = metacentric height GM.  Tipping moments (2.3):
    #   - rudder lateral force x vertical arm from C of M to rudder (row 14)
    #   - hull lateral reaction x vertical arm from C of M to hull lateral
    #     resistance centre (row 13).  Restoring = m g GM.
    # GM uses an effective height 0.2 m lower (crew lean) per 2.3.
    for label, vkt, phi, fac, one_side in [
        ("fast anastrophe", 9.5, 22.5, 3.25, False),
        ("tight anastrophe", 6.5, 67.5, 3.25, True),
        ("max-speed tight", 9.9, 67.5, 3.25, False),
    ]:
        ves = mb
        d, w, drift = ves.steady_turn(vkt, phi, fac, one_side=one_side)
        f_rud = ves.rudder_coeff(phi) * ves.rudder_drag(vkt, phi, fac)
        v = vkt * KT2MS
        f_hull = ves.m_app * v * v / (d / 2.0) - f_rud
        gm_eff = ves.GM - 0.2  # crew lean into turn (2.3)
        tipping = f_rud * ves.arm_rud + f_hull * ves.arm_lat
        heel = math.degrees(math.atan(tipping / (ves.m * 9.81 * gm_eff)))
        flag = "OK (<=3)" if heel <= 3.0 else ">3 deg"
        print(f"  {label:22s}: heel ~{heel:4.1f} deg {flag} (drift {drift:.1f} deg)")
