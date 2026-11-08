# Pre-registration — K-SCO-L1 (Scotland League One cards model)

Frozen: 2026-11-10, before any fitting. Branch `build/sco-league-one`.
Design authority: `analysis/MODEL_DESIGN.md` (K-SCO-L1); features X5;
evidence EDA (event yellows for 0.388 / against 0.535).
Reference: production `model_cards.py`; sibling analogue
`league/SCO-Championship/prereg/PREREG_K_SCOCH.md` — the architecture
(team yellow ratings + count distribution + naive ensemble
structure of the reference) is carried over in form; mirror the
shared constants, changing only league, seasons, line and the
target-source note below. The K harness follows the Championship
implementation shape (`engine/cards/model.py` + `harness.py`):
per-match chronological predict-then-update, date-grouped
(same-date matches never see each other), NB size `r` estimated
once from the warm-up predictions by the method-of-moments
estimator, separately for model/base/naive; the virgin `r` is
re-estimated from the pre-virgin warm-up predictions while the
Online state continues through virgin.
Phase rule (frozen): all rows are phase `regular`; no phase feature.
Calibration = **actual − predicted** everywhere in this build.

- Target: total event Yellow cards = `yellow_home + yellow_away`
  in the league CSV. Target-source decision (frozen here, before
  fitting): the stats feed carries NO `yellow_cards` key in any of
  the 969 payloads, so there is no stats-vs-events conflict to
  resolve; the target is the event-feed Yellow count by
  construction for the whole corpus. `YellowRed` events are NOT
  yellows under this definition (counted as reds). Primary line
  **3.5** (dev-period over-rate 0.4685, closest to 0.5; the 2.5
  over-rate is 0.7000, the 4.5 over-rate is 0.2852). Ladder
  2.5/3.5/4.5 reported.
- Reference constants (production `model_cards.py`, frozen):
  HL = 270 days, prior shrinkage K = 8 match-equivalents,
  venue-split attack/defence yellow ratings with exponential
  decay, league-mean fallback FB_MU_H = 2.15 / FB_MU_A = 1.95
  for a zero-card opening observation, Negative Binomial count
  distribution. No referee term: X8 is DROPPED (0 usable
  referees in 969 payloads).
- Arms: **Gate Zero only** (reference unmodified; referee not
  used). No variant arms are built.
- Training seed 2021/2022; dev 2022/2023–2024/2025 (n = 540 — the
  event target exists for every match); dev harness must not read
  2025/2026 / 2026/2027 rows.
- Baselines: league base rate; naive trailing-10 through the same
  count distribution as the reference harness.
- Virgin: 2025/2026 (n = 180), read ONCE, only if Gate Zero passes
  the dev gate. Calibration at 3.5 = mean actual − predicted,
  SE = sd(y_i − p_i)/√n.
- Halves: presentation only via the frozen event-derived yellows
  constant 0.3141 (1H/2H ladders on PASS, exactly as SCO-Premiership
  K-SCO).

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@3.5 beats BOTH baselines (league base rate; naive trailing-10), else the candidate is dead, no virgin read. Virgin legs — (i) LL@3.5 ≤ best baseline's; (ii) calibration |actual − predicted| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) no sign check (single arm). If Gate Zero passes all legs it ships; if any leg fails, K-SCO-L1 verdict is FAIL and nothing ships.

Mechanical reading: Gate Zero passes iff it survives the dev gate
AND passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as
such). Gate Zero dev failure ⇒ FAIL, virgin NOT read.

## Outputs

Engine `engine/cards/`; `results_dev.json` (+ per-match
`results_dev.csv`, force-added: one row per scored match with
per-match probabilities — NOT a per-season summary table);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/k_sco_l1_virgin_predictions.csv` (FT ladder 2.5/3.5/4.5;
1H/2H presentation-only via frozen yellows constant 0.3141, lines
1H 0.5/1.5/2.5, 2H 1.5/2.5/3.5). Verdict `reports/K_SCO_L1_VERDICT.md`.
Production code untouched. No push. No merge.
