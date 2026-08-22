"""One trireme oar, time-stepped (Phase 1 — the LL skeleton).

Kinematics (piecewise-linear in oar angle over the stroke cycle, matching the
rigid-oar model's convention):

  - drive:     C: +B/2 -> -B/2 at constant omega over t_drive (Table 9.6),
               blade immersed;
  - recovery:  -B/2 -> +B/2, blade out of water, no force.

Angle-based: the oar advances its angle at the *effective* omega each step, so
the physiology layer (ll/rower.py) can configure a force-limited stroke
(slower drive, shorter sweep, lost tempo) per catch via configure_stroke().
With the commanded kinematics configured (the default) the discretisation
reproduces the rigid-oar model exactly (Gate 1).

Force-driven mode (force=True — Plan 1, the force-driven oar): the drive's
kinematics EMERGE from the torque-balance EOM

    I·theta_ddot = -dir·Fh·lin - sign(omega)·|Fn|·l_cp      (blade in)

with the rower's constant demand force Fh (the chain's mean pull 7.43·r, or
Fh_BURST under spoude) and the flat-plate blade force Fn (ll/blade.py). The
oar settles where the blade drag exactly absorbs the demand (the drive
equilibrium vn = -sqrt(Fh·lin/(k·l_cp)) — never a stall), so the emerging
drive time sits near Table 9.6 (the G5-7 companion's physics: the measured
stroke IS the force-balanced stroke). The catch flip (the reversal in the
air, pinned at the catch, the spike force over t_rise) delivers the blade
entry at the equilibrium speed; the recovery stays kinematic. The crew
configures the demand/flip/entry/recovery per stroke (configure_force); the
emerging in-water time is telemetry (t_drive_last). mit <= 0 degenerates to
the instantaneous equilibrium (the blade at vn = -vn_eq exactly).

Force: flat-plate normal law (ll/blade.py). Massless lever for Gate 1; the
inertia layer (Table 3.1) lands later per the the LL design (simulation/AGENTS.md).

Deterministic: oar state is (C, in_drive, cycle_no) — a pure function of time.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from ll.blade import blade_force


@dataclass(frozen=True)
class OarStep:
    """Per-step telemetry (deterministic, replayable)."""
    t: float             # seconds since the last catch
    C: float             # oar angle from athwartships (rad)
    omega: float         # angular rate (rad/s)
    immersed: bool
    vn: float            # normal flow at blade CP (m/s)
    Fn: float            # blade force magnitude (N)
    Fx: float            # force on hull, along keel (N)
    Fy: float            # force on hull, athwartships (N)
    Fh: float            # handle force (N)


class Oar:
    def __init__(self, rig: dict, r_spm: float, t_drive: float | None = None,
                 direction: int = 1, mit: float = 0.0, t_rise: float = 0.15,
                 sweep_factor: float = 1.0, station: tuple | None = None,
                 force: bool = False):
        """direction = +1 forward stroke; -1 backing water (drive sweeps the
        other way — the blade force law then gives negative thrust naturally).

        mit: rotational inertia about the thole (kg m2, Table 3.1) — the
        inertia layer (Gate 5): at the catch the rower flips the oar from the
        recovery swing to the drive speed over t_rise (a handle-force spike);
        at the finish the oar's momentum assists (a release). The impulses
        are internal to the rower-oar system: the hull forces are unchanged.
        mit = 0 disables the layer (exact pre-Gate-5 behaviour).

        force: the Plan-1 force-driven drive — the drive's kinematics emerge
        from the torque-balance EOM (the module docstring); the flip is a
        real phase (pinned at the catch, the spike force over t_rise — the
        G5 layer's impulse convention, now a motion); the recovery stays
        kinematic. The crew configures the demand/flip/entry/recovery per
        stroke (configure_force); the emerging drive time is telemetry
        (t_drive_last). Kinematic mode: the validated constant-omega drive.

        station: (x, y, side) — the per-station layer (ll/stations.py):
        the blade's flow includes the ship's (u, v, r) at the station
        and the starboard oar's sweep mirrors (C_eff = -C)."""
        self.station = station
        self.rig = rig
        self.dir = direction
        self.mit = mit
        self.t_rise = t_rise
        self.force = force
        self._l_cp = rig["lout"] - (rig["blade"] - 0.260)   # blade CP
        # the force-driven mode's per-stroke inputs (configure_force) and
        # telemetry: the emerging in-water drive time and the entry speed
        self.fh_demand = 0.0          # N — the drive's constant demand
        self.fh_flip = 0.0            # N — the catch-flip force (the spike)
        self.omega_entry = 0.0        # rad/s — blade-entry |omega|
        self.in_flip = False
        self._flip_t = 0.0
        self._drive_t = 0.0
        self.t_drive_last = 0.0       # s — the last drive's in-water time
        self.omega_now = 0.0          # rad/s — the oar's instantaneous rate
        self.cycle = 60.0 / r_spm
        self.t_drive = t_drive if t_drive is not None else self.cycle * 0.333
        self.t_recovery = self.cycle - self.t_drive
        self.sweep = math.radians(rig["sweep"]) * sweep_factor  # tier sweep
        self.omega_cmd = self.sweep / self.t_drive        # commanded drive speed
        self.omega_rec_cmd = self.sweep / self.t_recovery
        # effective kinematics (the crew model may override per stroke)
        self.omega_drive = self.omega_cmd
        self.omega_recover = self.omega_rec_cmd
        self.sweep_eff = self.sweep
        self.C = self.dir * self.sweep / 2.0              # at the catch
        self.in_drive = True                              # first drive starts now
        self.t_since_catch = 0.0
        self.cycle_no = 0

    # ------------------------------------------------------------------
    def inertia_fh(self) -> float:
        """Handle-force contribution of the oar's rotational inertia (N):
        the catch flip (+I·(w_d+w_r)/(t_rise·lin), last t_rise of the cycle,
        blade out of the water) and the finish release (-same, first t_rise
        after the finish). Rectangular pulses delivering the exact impulse;
        net impulse over the cycle = 0 (energy closure)."""
        if self.mit <= 0.0:
            return 0.0
        if self.t_since_catch >= self.cycle - self.t_rise:
            return (self.mit * (self.omega_drive + self.omega_recover)
                    / (self.t_rise * self.rig["lin"]))
        if self.t_drive <= self.t_since_catch < self.t_drive + self.t_rise:
            return (-self.mit * (self.omega_drive + self.omega_recover)
                    / (self.t_rise * self.rig["lin"]))
        return 0.0

    def flip_power(self, rate_eff: float) -> float:
        """W/man the flip costs: 1/2·I·w_drive^2 per stroke (concentric;
        the finish braking is eccentric — cheaper — noted, not counted).
        Force-driven mode: the flip's kinetic energy is 1/2·I·w_entry^2
        (the entry speed the spike delivers)."""
        if self.mit <= 0.0:
            return 0.0
        w = self.omega_entry if self.force else self.omega_drive
        return 0.5 * self.mit * w * w * rate_eff / 60.0

    def reset(self) -> None:
        self.omega_drive = self.omega_cmd
        self.omega_recover = self.omega_rec_cmd
        self.sweep_eff = self.sweep
        self.C = self.dir * self.sweep / 2.0
        self.in_drive = True
        self.in_flip = False
        self._flip_t = 0.0
        self._drive_t = 0.0
        self.omega_now = 0.0          # the first drive starts from rest
        self.t_since_catch = 0.0
        self.cycle_no = 0

    def configure_stroke(self, omega_drive: float, omega_recover: float,
                         sweep_eff: float) -> None:
        """Set the effective kinematics for the next drive (called at the
        catch by the crew model — ll/rower.py)."""
        self.omega_drive = omega_drive
        self.omega_recover = omega_recover
        self.sweep_eff = sweep_eff

    def configure_force(self, fh_demand: float, fh_flip: float,
                        omega_entry: float, omega_recover: float,
                        sweep_eff: float) -> None:
        """Set the force-driven stroke (called at the catch by the crew —
        ll/rower.py): the drive's constant demand, the flip force (the spike
        over t_rise), the blade-entry |omega|, the recovery speed, the sweep.
        The drive's kinematics are NOT configured — they emerge from the EOM."""
        self.fh_demand = fh_demand
        self.fh_flip = fh_flip
        self.omega_entry = omega_entry
        self.omega_recover = omega_recover
        self.sweep_eff = sweep_eff

    # ------------------------------------------------------------------
    # force-driven mode (Plan 1): the substep phase machine

    def _force_substep(self, h: float, V: float,
                       ship_state: tuple | None = None) -> OarStep:
        """Advance the force-mode phase machine by h; return the
        instantaneous forces. Phases: recovery (kinematic, blade out) -> flip
        (pinned at the catch, the spike force over t_rise — the reversal in
        the air, the G5 impulse convention as a motion) -> drive (blade in,
        the EOM under the constant demand)."""
        if self.in_drive:
            # the drive: I·theta_ddot = -dir·Fh·lin - sign(omega)·|Fn|·l_cp
            flow = None
            C_eff = self.C
            if self.station is not None and ship_state is not None:
                x, y, side = self.station
                v, r = ship_state
                flow = (V, v, r, x, y)
                C_eff = side * self.C
            f = blade_force(C_eff, self.omega_now, V, self.rig, True,
                            flow=flow)
            # the blade's drag opposes the blade's motion RELATIVE TO THE
            # water: the moment is -Fn·l_cp with Fn = k·|vn|·vn (the signed
            # flat-plate force — the companion's exact form). At vn > 0 (the
            # blade slower than the flow — the parked blade at the catch)
            # the flow PUSHES the drive (the catch deadspot: holding it
            # would demand ~2 kN at the handle — the flip-in-air is why the
            # entry comes at the equilibrium speed); at vn < 0 the drag
            # opposes. The equilibrium vn = -dir·sqrt(Fh·lin/(k·l_cp))
            # attracts — never a stall.
            if self.mit > 0.0:
                acc = (-self.dir * self.fh_demand * self.rig["lin"]
                       - f["Fn"] * self._l_cp) / self.mit
                self.omega_now += acc * h
            else:
                # massless: the instantaneous equilibrium speed
                vn_eq = -self.dir * math.sqrt(
                    self.fh_demand * self.rig["lin"]
                    / (0.5 * 1025.0 * self.rig["area"] * 1.8 * self._l_cp))
                self.omega_now = (vn_eq - f["vn"] + self._l_cp
                                  * self.omega_now) / self._l_cp
            self.C += self.omega_now * h
            self._drive_t += h
            if self.dir * self.C <= -self.sweep_eff / 2:    # finish
                self.C = -self.dir * self.sweep_eff / 2
                self.in_drive = False
                self.t_drive_last = self._drive_t
                self._drive_t = 0.0
            return OarStep(t=self.t_since_catch, C=self.C,
                           omega=self.omega_now, immersed=True, vn=f["vn"],
                           Fn=f["Fn"], Fx=f["Fx"], Fy=f["Fy"],
                           Fh=self.fh_demand)
        if self.in_flip:
            # the pinned flip: C stays at the catch; the oar's rate goes
            # linearly from +dir·omega_recover to -dir·omega_entry under the
            # spike force (the EOM's closed form over t_rise)
            self._flip_t += h
            frac = min(1.0, self._flip_t / self.t_rise)
            w = self.dir * (self.omega_recover
                            - (self.omega_recover + self.omega_entry) * frac)
            self.omega_now = w
            if self._flip_t >= self.t_rise:
                self.in_flip = False
                self.in_drive = True
                self._drive_t = 0.0
                self.omega_now = -self.dir * self.omega_entry
            return OarStep(t=self.t_since_catch, C=self.C,
                           omega=self.omega_now, immersed=False, vn=0.0,
                           Fn=0.0, Fx=0.0, Fy=0.0, Fh=self.fh_flip)
        # the recovery (kinematic, as the commanded mode)
        self.C += self.dir * self.omega_recover * h
        if self.dir * self.C >= self.sweep_eff / 2:         # catch
            self.C = self.dir * self.sweep_eff / 2
            self.cycle_no += 1
            self.t_since_catch = 0.0
            if self.mit > 0.0:
                self.in_flip = True                         # the flip first
                self._flip_t = 0.0
            else:
                self.in_drive = True
                self._drive_t = 0.0
                self.omega_now = -self.dir * self.omega_entry
        return OarStep(t=self.t_since_catch, C=self.C,
                       omega=self.dir * self.omega_recover, immersed=False,
                       vn=0.0, Fn=0.0, Fx=0.0, Fy=0.0, Fh=0.0)

    def _step_force(self, dt: float, V: float,
                    ship_state: tuple | None = None) -> OarStep:
        """One ship step in force mode: substep the phase machine (the
        drive's EOM needs dt ~ 1e-3 — the blade-force stiffness ~50 s^-1)
        and return the MEAN forces over the step (the impulse-correct
        forcing for the hull), with the state at the step's end."""
        h = 0.001
        n = max(1, int(round(dt / h)))
        h = dt / n
        fx = fy = fh = 0.0
        vn = fn = 0.0
        s = None
        for _ in range(n):
            s = self._force_substep(h, V, ship_state)
            fx += s.Fx * h
            fy += s.Fy * h
            fh += s.Fh * h
            vn += abs(s.vn) * h
            fn += abs(s.Fn) * h
        self.t_since_catch += dt
        return OarStep(t=self.t_since_catch - dt, C=s.C, omega=s.omega,
                       immersed=s.immersed, vn=vn / dt, Fn=fn / dt,
                       Fx=fx / dt, Fy=fy / dt, Fh=fh / dt)

    def step(self, dt: float, V: float, ship_state: tuple | None = None) -> OarStep:
        if self.force:
            return self._step_force(dt, V, ship_state)
        C = self.C
        immersed = self.in_drive
        omega = (-self.dir * self.omega_drive if immersed
                 else self.dir * self.omega_recover)
        flow = None
        if self.station is not None and ship_state is not None:
            x, y, side = self.station      # y signed (port +, star -)
            v, r = ship_state
            flow = (V, v, r, x, y)
            C_eff = side * C               # the starboard sweep mirrors
        else:
            C_eff = C
        f = blade_force(C_eff, omega, V, self.rig, immersed, flow=flow)
        # the inertia pulses (blade out of the water at the stroke ends)
        f["Fh"] = f["Fh"] + self.inertia_fh()
        # advance
        if self.in_drive:
            self.C -= self.dir * self.omega_drive * dt
            if self.dir * self.C <= -self.sweep_eff / 2:   # finish
                self.C = -self.dir * self.sweep_eff / 2
                self.in_drive = False
        else:
            self.C += self.dir * self.omega_recover * dt
            if self.dir * self.C >= self.sweep_eff / 2:    # catch
                self.C = self.dir * self.sweep_eff / 2
                self.in_drive = True
                self.cycle_no += 1
                self.t_since_catch = 0.0
        self.t_since_catch += dt
        return OarStep(t=self.t_since_catch - dt, C=C, omega=omega,
                       immersed=immersed, vn=f["vn"], Fn=f["Fn"], Fx=f["Fx"],
                       Fy=f["Fy"], Fh=f["Fh"])


def simulate(oar: Oar, V: float, dt: float, n_cycles: int) -> dict:
    """Run n_cycles at fixed hull speed V; return cycle-averaged quantities
    in the rigid-oar model's conventions (mean thrust over the full cycle,
    handle force RMS over the drive, ideal blade efficiency)."""
    oar.reset()
    Fx_sum = Fh2 = Ft = Th = 0.0
    fb_peak = 0.0
    while oar.cycle_no < n_cycles:
        s = oar.step(dt, V)
        if s.immersed:
            Fx_sum += s.Fx * dt
            Fh2 += s.Fh * s.Fh * dt
            Ft += s.Fx * V * dt
            Th += s.Fh * abs(s.omega) * oar.rig["lin"] * dt
            fb_peak = max(fb_peak, abs(s.Fn))
    return dict(
        mean_thrust=Fx_sum / (oar.cycle * n_cycles),
        mean_fh=math.sqrt(Fh2 / (oar.t_drive * n_cycles)),
        eff=Ft / Th if Th else float("nan"),
        fb_peak=fb_peak,
    )
