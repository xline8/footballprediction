# Verdict — G-KZ (KZ-PremierLeague goals, Dixon–Coles goals-only)

**PASS — PROVISIONAL on both virgin calibration legs. Gate Zero ships.**

Dev (season-blocked walk-forward; train seed 2021, 182 finished matches;
pooled n = 702):

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | 1.0290 | 0.2135 | 0.6819 |
| SHRINK | 1.0290 | 0.2135 | 0.6819 |
| Climatology | 1.0712 | 0.2285 | 0.6929 |
| Naive trailing-10 | 1.0952 | 0.2318 | 0.7200 |

Per-season Gate Zero vs climatology (1X2 LL / RPS / OU2.5 LL):

| Season | n | Gate Zero | Climatology |
|---|---|---|---|
| 2022 | 182 | 1.0576 / 0.2263 / 0.6662 | 1.0641 / 0.2295 / 0.6959 |
| 2023 | 182 | 1.0638 / 0.2235 / 0.7001 | 1.0718 / 0.2297 / 0.6923 |
| 2024 | 156 | 1.0010 / 0.2060 / 0.6736 | 1.0652 / 0.2281 / 0.6862 |
| 2025 | 182 | 0.9896 / 0.1971 / 0.6866 | 1.0829 / 0.2266 / 0.6961 |

Gate Zero beats climatology on pooled 1X2 LL in every dev season, and
on pooled RPS in every season. The 2022 margin is narrow (LL by
0.0065) but the 2024–2025 margins are wide (0.064–0.093), and the
pooled win is 0.0422 on LL. The one soft spot is OU2.5 in 2023, where
Gate Zero loses to climatology (0.7001 vs 0.6923) — the only
season-metric loss in the dev table. The naive trailing-10 baseline is
worse than the DC pooled on every metric (LL 1.0952), so the ratings
add real signal beyond recent form — consistent with the EDA's
unusually strong attack trait (goals-for split-half r=0.802). Rho is
0.0 in all four dev fits; mu runs 1.23–1.33. SHRINK is byte-identical
to Gate Zero in every season (0 changed rows, 0 thin-history teams),
exactly as EDA F13 predicted: every target-season team has either 0
or ≥24 prior in-league matches.

Virgin (2026, complete season, n = 240; fit on 2021–2025, n = 884,
cutoff 2026-03-07, rho 0.0, mu 1.3373, h 0.2543):

| Arm | 1X2 LL | RPS | OU2.5 LL | Climatology LL |
|---|---|---|---|---|
| Gate Zero | 1.0152 | 0.2056 | 0.6873 | 1.0678 |
| SHRINK | 1.0152 | 0.2056 | 0.6873 | 1.0678 |

Calibration (mean predicted − actual, n = 240; actual home-win rate
0.4583, OU2.5 over-rate 0.5042):

| Arm | Home-win diff | OU2.5 diff |
|---|---|---|
| Gate Zero | −1.26pp (SE 3.09pp) | −3.21pp (SE 3.21pp) |
| SHRINK | −1.26pp (SE 3.09pp) | −3.21pp (SE 3.21pp) |

Gate arithmetic (PREREG_G_KZ): dev gate — pooled 1X2 LL beats
climatology ✓ (1.0290 < 1.0712); pooled RPS beats climatology ✓
(0.2135 < 0.2285); pooled OU2.5 LL beats the base-rate baseline ✓
(0.6819 < 0.6929). Virgin leg (i) LL — 1.0152 ≤ Gate Zero's own
(equal) and ≤ climatology's 1.0678 ✓. Virgin leg (ii) calibration —
home-win |−1.26pp| breaches the 1.0pp boundary by 0.26pp, within 1 SE
(3.09pp) → PROVISIONAL PASS; OU2.5 |−3.21pp| breaches by 2.21pp,
within 1 SE (3.21pp) → PROVISIONAL PASS. The OU2.5 leg is provisional
by a thinner margin than the home-win leg (excess 2.21pp against an
SE of 3.21pp): the model under-predicts the 2026 over-rate (mean
predicted 0.472 vs actual 0.504), and with n=240 the SE is wide
enough to carry it. That is what the frozen rule says, and it is
recorded here as provisional, not clean — the daily runner's live
grading will be the real test of whether the OU2.5 level is biased
or this was a noisy season. Virgin leg (iii) sign check — SHRINK's
dev LL ≤ Gate Zero's in 4/4 dev seasons (equal) ✓. Both-pass rule:
both arms pass, pooled virgin LLs tie, so the simpler arm ships:
**Gate Zero**.

Ships: Gate Zero arm with the virgin fitted params
(`engine/goals/fitted_params_virgin.json`: rho 0.0, mu 1.3373,
h 0.2543, 22 teams — the two 2026 entrants, Altai Semey and Irtysh
Pavlodar, start at the league mean, a = d = 0) and the virgin predictions
(`predictions/g_kz_virgin_predictions.csv`, 240 rows, FT 1X2 / OU /
BTTS plus 1H/2H presentation via the frozen goals constant 0.4539).
SHRINK ships nothing separately — it is identical to Gate Zero
everywhere it was measured.

## Independent-verification notes (build log)

- Production-DC replay (`/tmp/replay_g_kz.py`, `model_v2.DC`, hl = 270,
  same season-blocked cutoffs): per-season Gate Zero LL/RPS/OU match
  the harness to 4 decimals; worst per-match probability difference
  vs `results_dev.csv` is 0.00005 (CSV rounding). Rho matches per
  season (0.0 throughout).
- Virgin replay (`/tmp/replay_g_kz_virgin.py`, same production DC,
  fit 2021–2025, predict 2026): LL/RPS/OU, climatology scores, and
  both calibration diffs + SEs match `results_virgin.json` exactly
  to 6 decimals. The virgin numbers are a property of the league,
  not an implementation artefact.
- Pooled numbers recomputed from `results_dev.csv` (702 rows, seasons
  2022–2025 only, no 2026 string anywhere): identical to
  `results_dev.json`. SHRINK differs from Gate Zero on 0/702 rows.
- Predictions file checked: 240 rows, Gate Zero only, halves splits
  exact (1H = 0.4539·FT λ, 2H = 0.5461·FT λ, 0 bad rows),
  probabilities sum to 1 on all rows; mean predicted home-win 0.4457
  and over-2.5 0.4720 reproduce the calibration diffs against the
  actual 0.4583 / 0.5042.
- Harness re-run by Codex is byte-identical (JSON + CSV, sha256
  diffed across two runs).
- Defects found and fixed during the build:
  1. EDA `entrants` used `prev = cur` (previous season only) instead
     of the accumulated union, so returnees (e.g. FC Turan, Okzhetpes)
     were misclassified as entrants. Fixed to `prev |= cur` before
     the prereg; the corrected dev entrant set is n=6 (Maktaaral,
     Aksu, Okzhetpes, Yelimay, Zhenis, Ulytau). Conclusion unchanged
     (descriptive only, no X2 arm).
  2. The `virgin-predict` step overwrote `results_virgin.json` with
     the Gate Zero arm only, dropping the SHRINK virgin entry that
     `virgin-metrics` had computed. Fixed by restoring the SHRINK
     entry from that run's reported numbers (identical to Gate Zero
     to 6 decimals, and provably identical: every 2026 team has 0 or
     ≥26 prior matches, so the shrink factor is 0 for the two
     entrants — the same as Gate Zero's unseen rule — and 1 for
     everyone else). The restore is recorded in the file's
     `shrink_note` field. Upstream note: the J1 harness has the same
     overwrite behaviour; leagues that run `virgin-predict` should
     expect it.
  3. The 24 GB `fotmob_world` tree is untracked, so a git worktree
     does not contain it: `build_data.py` / `eda.py` resolve the
     warehouse against the main checkout
     `~/workspace/footballprediction` when the worktree lacks it
     (read-only). No files were written outside the worktree.
- No Codex defects found in the engine/dev/virgin run itself; the
  two Codex briefs and their outputs are in
  `~/workspace/agent-briefs/kz-g-engine-brief.md` and
  `kz-g-virgin-brief.md`.

## What this means for the league

G-KZ is the league's only buildable candidate (SOT, corners, cards,
total shots all have no target in any season), and it PASSES —
provisionally on calibration. That contrasts with UY-SegundaDivision,
whose Gate Zero lost to climatology on all three dev legs. The pass rests on a
genuinely strong attack trait, but the OU2.5 calibration is the
honest weak point: −3.21pp on the virgin read, carried only by the
wide n=240 SE. If live grading shows the OU2.5 level biased rather
than noisy, that leg — not the 1X2 model — is where a future
re-registered attempt should look.
