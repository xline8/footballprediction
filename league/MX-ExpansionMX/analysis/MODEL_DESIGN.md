# Step 6 — Model Design: Mexico Liga de Expansión MX candidates

Feature set: `FEATURES.md` (J1 X1–X9 template, verdicts measured in
this league — X1/X2/X3/X4/X6/X7/X8/X9 all dropped on this league's
evidence; altitude R7 rejected on measurement). Structure: this
league's own engine under `league/MX-ExpansionMX/engine/`, seeded
from the proven reference implementations (CL-LigaDeAscenso goals
port; J1 cards port) and diverging only as written here, through
this league's own gates. Calibration = actual − predicted
everywhere.

## Feasibility matrix

| candidate | target exists in data? | valid virgin contains target? | scorable dev window contains target? | verdict at design |
|---|---|---|---|---|
| G-MXE goals | yes — scores, all blocks | yes (105) | yes (967) | **BUILD** |
| S-MXE SOT | only in in-progress 2026/2027 (128 rows) | no — no complete season has it | no (0 rows) | **NOT BUILDABLE** |
| C-MXE corners | only in in-progress 2026/2027 | no | no (0 rows) | **NOT BUILDABLE** |
| T-MXE total shots | only in in-progress 2026/2027 | no | no (0 rows) | **NOT BUILDABLE** |
| K-MXE cards | yes — event yellows, clean era 2023/2024+ | yes (105) | yes (420 scored after warm-up) | **BUILD** |

S/C/T get verdict documents recording NOT BUILDABLE with the era
evidence; no prereg is written and nothing is fitted for them.

## Shared frame (goals)

- Blocks: 10 chronological tournament blocks, regular phase only.
  2026/2027 - Apertura is in progress and excluded wholesale
  (reserved confirmatory).
- Warm-up/seed: block 1 (2021/2022 - Apertura, n=136).
- Dev: tournament-blocked walk-forward, scored blocks 2–9 (n=967).
- Virgin: 2025/2026 - Clausura regular (n=105, complete), read
  ONCE, only for arms passing the dev gate.
- Baselines: climatology (pooled outcome rates + OU2.5 over-rate of
  all blocks strictly before the target block).
- Gate legs (program-wide): dev gate vs baselines; virgin (i) LL
  leg, (ii) calibration |breach| ≤1.0pp clean PASS, ≤1 SE =
  PROVISIONAL PASS, else FAIL, (iii) per-block sign check for
  variant both-pass. Both-pass → lower pooled virgin LL ships;
  ties → simpler arm. If Gate Zero fails its dev gate, variants
  are moot and the virgin is NOT read.

## G-MXE — goals

Reference: production Dixon-Coles (model_v2 `DC` pattern as ported
in CL-LigaDeAscenso), **goals-only** (X1 dropped), hl=270, rho grid
(0, −0.05, −0.10, −0.15), 14 sweeps, damping 0.7, +0.25 smoothing.
Arms: **Gate Zero**; **SHRINK** (sanctioned G-J2-lesson arm: for a
team with <6 prior in-league training matches, ratings scaled by
n/6 at prediction time; expected bite ≈ 0 under tournament-blocked
fitting — entrants have exactly 0 — and that is itself a recorded
finding if so). No X2 arm (no mover flow exists, FEATURES.md). No
altitude arm (R7 — measured absent here). Primary line OU 2.5
(pooled dev over-rate ≈ 0.50) + 1X2 LL/RPS.

## K-MXE — cards

Reference: production cards pattern as ported in J1 (decayed
venue-split team ratings shrunk to league means, HL=270, K=8; NB
total with r estimated on the warm-up block; Gate Zero is the only
arm — X8 dropped, referee coverage 0% in dev). Target: unified
event yellows (Yellow + YellowRed). Corpus restriction (frozen):
clean era only — warm-up = 2023/2024 - Apertura (n=105, unscored,
also the r-estimation block); dev scored online walk-forward over
2023/2024 - Clausura, 2024/2025 - Apertura, 2024/2025 - Clausura,
2025/2026 - Apertura (n=420); virgin = 2025/2026 - Clausura
(n=105), read ONCE only if the dev gate passes. The harness is the
production online pattern (predict-then-update, strictly
chronological), scored per block for reporting. Baselines scored
alongside: league base rate and naive trailing-10. **Primary line
5.5** — fixed from the dev distribution (dev mean 5.169; over-rates
3.5→0.779, 4.5→0.598, 5.5→0.421; 5.5 is nearest the median; ladder
4.5/5.5/6.5 scored). Dev gate: pooled dev model LL at 5.5 must beat
BOTH baselines. Virgin legs as in the shared frame, applied to the
5.5 line (LL leg vs Gate Zero's own components = base and naive;
calibration leg on the over-5.5 rate).

## Halves presentation (on PASS only)

FT + 1H/2H via frozen constants: goals 0.448, yellows 0.402.
SOT/corners/total shots ship nothing and have no constants.

## Global forbidden list

The J.League MODEL_DESIGN §7 list applies verbatim: no half-share
modelling, no absence features, no finishing/conversion covariates,
no altitude feature (R7), no post-match snapshot features, no
feature without a reliability check in this league's EDA, no
post-hoc arms.
