# Phase 6 — Model Design: PT-LigaPortugal candidates

Five candidates — every market clears the feasibility matrix:
the target exists in the data in every season (stats and shotmap
100%), and the virgin window (2026/2027, transitional, n=98)
contains every target.

**Shared frame.** Dev = expanding, season-blocked walk-forward:
fit on all seasons before the target season, evaluate on
2022/2023, 2023/2024, 2024/2025, 2025/2026 (pooled n=1,224).
Virgin = 2026/2027 (n=98, TRANSITIONAL — in progress; a season-end
confirmatory read is reserved and this read is labelled as such in
every verdict). Virgin is read ONCE, only for arms that pass the
dev gate. Baselines: league base rate / climatology (per target
season, from prior seasons only) and naive trailing-10 (count
markets). Gate legs are the program's frozen ones (see each
prereg): dev gate beats both baselines on the primary line;
virgin (i) LL ≤ Gate Zero's and ≤ best baseline's, (ii) calibration
|breach| ≤ 1.0pp clean PASS, ≤ 1 SE PROVISIONAL PASS, else FAIL,
(iii) variant sign check ≥ half the dev seasons. Both-pass → lower
virgin LL ships; tie → Gate Zero.

**Primary lines** (from the dev distribution): goals OU 2.5;
SOT 8.5 (dev mean 8.41); corners 9.5 (9.99); cards 4.5 (5.16);
total shots 24.5 (24.90).

## G-PT — goals (reference: production Dixon-Coles + xG blend)

Arms: **Gate Zero** (DC pattern copied from the production/J1
engine pattern: blend 0.5·goals + 0.5·xG — fallback never triggers,
xG is complete — HL 270, rho grid, season-blocked fit) and
**Arm SHRINK** (the template-sanctioned G-J2 lesson): after the
Gate Zero fit, the attack/defence ratings of any team with <15
training-window matches are scaled by 0.5 toward the league mean
before predicting that season. X2's tier offset is dropped
(FEATURES.md) — no tier corpus; X3 dropped (r=0.27).

## S-PT — SOT (reference: production `model_sot.py` v5 pattern)

Gate Zero: joint shots ratings (decay HL 365, shrinkage prior
K=8 match-equivalents) → expected shots per team; on-target ratio
per team shrunk with the v5 Beta-Binomial prior (200 pseudo-shots)
toward the league ratio; total SOT mu = Σ shots·ratio; NB with r
from the training window; final probability = 50/50 ensemble of the
model NB and the naive trailing-10 NB (v5's structure).
Variants: **X4** — the ratio is additionally tilted by the team's
xG-per-shot relative to the league (ratio-of-sums over the training
window, exponent 0.5, clamp [0.8, 1.25]); **X6** — same tilt using
attacking xGOT-per-shot instead, era-guarded: computed only from
2024/2025+ matches, arm inactive (≡ Gate Zero) for target seasons
whose training window holds <8 era matches per team on average —
in practice active only for 2025/2026 dev and the virgin fit, and
reported as such.

## C-PT — corners (reference: production `model_corners_v3` pattern)

Gate Zero: decay-weighted (HL 270) home/away corner base rates,
rolling-5 shots relative factors, gamma grid fitted per target
season on prior walk-forward rows, NB total, territorial multiplier
from X9 covariates (possession + big chances, betas on a grid,
clamp [0.70, 1.43]) — the C-J1 engine pattern. Variant **X7**:
multiplier covariates replaced by opp-box touches (training-window
team means, min 8 valid matches, else inactive).

## K-PT — cards (reference: production `model_cards.py` pattern)

Gate Zero: decay-weighted team yellow for/against rates shrunk to
the league mean, NB total (r from the training window). Variant
**X8**: mu multiplied by the appointed referee's shrunk yellow rate
÷ league rate (shrinkage 8 match-equivalents; referee unknown or
<8 prior matches → multiplier 1.0). Referee reliability here is
weak (r=0.28) — the arm is expected to have to earn its place.

## T-PT — total shots (reference: the shots v1 pattern, as T-J1 arm A)

Gate Zero (arm A): team shots for/against ratings (decay-weighted,
shrunk), NB total, 50/50 ensemble with naive trailing-10.
Variant **E9**: identical, except the NB size r is estimated from
the trailing 200 league matches before each target season instead
of the whole training window. (The v2 level layer is not run: the
program cap is 2–3 arms and T-J1's B arm failed its legs; the
level-layer question is not re-opened here.)

## Halves presentation

FT + 1H/2H via the frozen PT constants (goals 0.443, SOT 0.449,
corners 0.471, yellows 0.331, shots 0.456), presentation only, in
the predictions CSVs of passing candidates.

## Not candidates

None within the five standard markets — all five are feasible.
Red cards are never a target (program rule).
