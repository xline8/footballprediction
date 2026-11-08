# Verdict — G-SCO-L1 (Scotland League One goals)

**FAIL at the dev gate. Virgin NOT read. Nothing ships.**

Prereg: `prereg/PREREG_G_SCO_L1.md`. Dev n=540 (2022/2023–2024/2025,
season-blocked walk-forward). All numbers below were recomputed by
the builder from `engine/goals/results_dev.csv` (per-match rows) and
agree with `engine/goals/results_dev.json` to all printed digits.
Calibration = actual − predicted (not needed: the candidate died at
dev, before any calibration leg).

## Dev (pooled)

| arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | 1.0726 | 0.2309 | 0.7053 |
| SHRINK | 1.0726 | 0.2309 | 0.7053 |
| X2 | 1.0762 | 0.2309 | 0.7089 |
| climatology / base | 1.0775 | 0.2344 | 0.6868 |

Dev gate (verbatim): pooled 1X2 LL and RPS must beat climatology,
and OU2.5 LL must beat the base-rate baseline. Gate Zero beats
climatology on 1X2 LL (1.0726 < 1.0775) and RPS (0.2309 < 0.2344)
but LOSES the OU2.5 leg (0.7053 > 0.6868). Per-season 1X2 LL, Gate
Zero vs climatology: 1.0689 vs 1.0762, 1.0763 vs 1.0744, 1.0726 vs
1.0820 — the DC pattern beats climatology in two of three dev
seasons, but the OU2.5 leg fails in two of three (0.7237 vs 0.6872,
0.7032 vs 0.6745, 0.6888 vs 0.6988 — it wins only 2024/2025).
Gate Zero therefore fails its own dev gate; per the frozen
mechanical reading the variants are moot, the virgin (2025/2026)
is NOT read, and G-SCO-L1 is closed as FAIL. The not-read state is
recorded in `engine/goals/results_virgin.json`
(`{"virgin_read": false, ...}`).

SHRINK finding: numerically identical to Gate Zero on all 540 dev
rows — under season-blocked expanding fits every team at
prediction time has either 0 prior in-league matches (entrant;
n=0 ⇒ ratings = league mean in both arms) or ≥36, so the 1–5
match band never occurs. Recorded, as in G-SCOCH and G-RU1.

X2 finding: the arm was implemented CORRECTLY this time (the
G-SCOCH defect was not repeated): offsets apply only to each
target season's own entrants, magnitudes estimated from entrant
first seasons strictly before the target season. X2 ≡ Gate Zero
in 2022/2023 (max |Δp_home| = 0.0, offsets 0 with 0 history
clubs). Applied offsets: 2023/2024 down log-attack +0.1371 /
log-defence −0.2927 (ΔGF +0.2139 / ΔGA −0.3694, 2 history clubs),
up_other −0.0753 / +0.0226; 2024/2025 down +0.1348 / −0.2526
(ΔGF +0.2236 / ΔGA −0.3458, 4 history clubs), up_other −0.1331 /
+0.0617. The mover gap is real in EDA (pooled down ΔGF +0.176 /
ΔGA −0.288, consistent in all four seasons) but the X2 arm still
loses to climatology on 1X2 LL pooled (1.0762 vs 1.0775 is a win
on LL, but OU2.5 0.7089 vs 0.6868 fails) and loses to Gate Zero
on 1X2 LL in two of three dev seasons — it changes nothing
mechanically, since Gate Zero's dev failure closes the candidate
before any variant is considered.

No fitted params, no predictions. Production code untouched.
