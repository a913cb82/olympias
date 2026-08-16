"""The fast high-level simulator (the calibration protocol — simulation/AGENTS.md).

The HL is a curve-chasing ship: it reads its response curves from a
Calibration (hl/curves.py), chases the equilibrium speed with a first-order
lag, steers through calibrated turn diameters, and carries one W' tank.
No per-oar work, no hidden physics — and no numbers of its own: every
constant comes from the validated chain or a direct LL measurement.

    real-world data  ->  LL (the oracle)  ->  HL (approximation, labelled)
"""

from .curves import Calibration, bootstrap, default, load

__all__ = ["Calibration", "bootstrap", "default", "load"]
