# Verdict — S-UA (SOT): FAIL

Dev (valid stats n=462): GZ LL@6.5 0.6757, RS 0.6755; baselines
base rate 0.7038, naive 0.6835 — both arms passed the dev gate.
Virgin (2025/2026, valid stats n=223, read ONCE; independently
recomputed from predictions_virgin.csv, exact): GZ LL 0.6798, RS
0.6801 — leg (i) PASSED (best baseline 0.6950). Calibration: GZ
+5.63pp, RS +5.75pp (SE 3.29pp; boundary 4.29pp) — leg (ii) FAIL
for both arms. The virgin season's SOT level rebounded to
7.21/match after the cold 2024/2025 (5.77) inside the training
window. **FAIL — nothing ships.** FT-only market; no halves.
Defect noted: 3 dev rows carry zero-filled shots/SOT with real
corners; they count as valid under the frozen row-level stub rule
and stand in the scored set as frozen (n=462 as preregistered).
