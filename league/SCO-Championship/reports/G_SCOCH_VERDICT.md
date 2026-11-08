# Verdict — G-SCOCH (Scotland Championship goals)

**FAIL at the dev gate. Virgin NOT read. Nothing ships.**

Prereg: `prereg/PREREG_G_SCOCH.md`. Dev n=540 (2022/2023–2024/2025,
season-blocked walk-forward). All numbers below were recomputed by
the coordinator from `engine/goals/predictions_dev.csv` and the
league CSV.

## Dev (pooled)

| arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | 1.1055 | 0.2369 | 0.7222 |
| SHRINK | 1.1055 | 0.2369 | 0.7222 |
| X2 (as implemented — see defect) | 1.0922 | 0.2351 | 0.7227 |
| climatology / base | 1.0873 | 0.2314 | 0.6998 |

Dev gate (verbatim): pooled 1X2 LL and RPS must beat climatology
AND OU2.5 LL must beat the base-rate baseline. Gate Zero fails all
three legs (1.1055 > 1.0873; 0.2369 > 0.2314; 0.7222 > 0.6998).
Per-season 1X2 LL, Gate Zero vs climatology: 1.1306 vs 1.0921,
1.1148 vs 1.0967, 1.0711 vs 1.0731 — the DC pattern beats
climatology in only one of three dev seasons. Gate Zero therefore
fails its own dev gate; per the frozen mechanical reading the
variants are moot, the virgin (2025/2026) is NOT read, and
G-SCOCH is closed as FAIL.

SHRINK finding: numerically identical to Gate Zero on all 540 dev
rows — under season-blocked expanding fits every team at
prediction time has either 0 prior in-league matches (entrant;
n=0 ⇒ ratings = league mean in both arms) or ≥36, so the 1–5
match band never occurs. Recorded, as in G-RU1.

## Defect (stated plainly)

The X2 arm as implemented by the builder is NOT the frozen X2:
`engine/goals/harness.py` builds the mover set from all entrant
seasons strictly before the target season and applies the offsets
to those past entrants, whereas PREREG_G_SCOCH freezes the offset
application to the target season's own entrants (with magnitudes
estimated from past transitions). The X2 dev row above is
therefore not a valid reading of the registered arm. It changes
nothing mechanically: Gate Zero's dev failure closes the
candidate before any variant is considered, and even the invalid
X2 row (1.0922) still loses to climatology (1.0873) on the 1X2
leg. No re-run was performed — rescuing a variant after a Gate
Zero dev failure is exactly what the frozen rules forbid. The
underlying X2 evidence stands as measured in EDA (entrants from
the Premiership: ΔGF +0.388 / ΔGA −0.408, consistent in all four
seasons) for any future prereg.

No fitted params, no predictions. Production code untouched.
