import sys
sys.path.insert(0, "/home/acbraith/projects/olympias/research/lane-4-oars")
from lane4_propulsion import hull_power, speed_from_power, oar_power, mean_pull, KT

# Table 1.2.1 (Rankov 2012 ch.1.2): SPM -> knots during one 1992 acceleration run.
# Crew ~154 (of 170) at trial start; later ran with ~135 / 121.
pairs = [(38,5.8),(41,6.0),(42,5.9),(43,6.2),(44,6.3),(45,6.6),(45,6.9),
         (44,7.2),(45,7.4),(47,8.0),(46,8.1)]

# Pull duration t_pull s (Table 9.6) -> E = 1/(1+q/p); use sprint E=0.730.
E = 0.730
L = 0.78   # Olympias effective pull length at butt (m)

print(f"{'spm':>4} {'obs_kt':>7} | n=170          n=154          n=135          n=121")
for spm, obs in pairs:
    P = mean_pull(spm)
    row = f"{spm:4d} {obs:7.1f} |"
    for n in (170, 154, 135, 121):
        W = oar_power(n, P, L, spm, E)
        V = speed_from_power(W, hull=1.0)   # Olympias hull
        row += f" {V/KT:10.2f}"
    print(row)
