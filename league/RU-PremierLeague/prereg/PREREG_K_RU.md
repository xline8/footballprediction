# Pre-registration — K-RU (RU-Premier League cards model)

Frozen: 2026-11-10, before any fitting. Branch `build/ru-premier`.
Design authority: `analysis/MODEL_DESIGN.md` (K-RU); features X5;
evidence EDA (event yellows for 0.545 / against 0.645). Reference:
production `model_cards.py`; PL analogue `PREREG_K_PL.md` and the J1
K engine (`league/J1/engine/cards/`) — the architecture (team yellow
ratings + count distribution + naive ensemble structure of the
reference) is carried over in form; mirror the shared constants,
changing only league, seasons, line and target source below.
Phase rule (frozen, MODEL_DESIGN): all rows are phase `regular`;
no phase feature anywhere.
Calibration = **actual − predicted** everywhere in this build.

- Target: EVENT-UNIFIED yellows = `ev_yellow_home + ev_yellow_away`
  (event Yellow + YellowRed per team, from the match events feed).
  The stats-vs-events artefact is PRESENT in this league (exact
  agreement 76.5%, mean stats − events = −0.550, stats lower in
  21.7% vs higher in 1.8%, max |diff| 11), so the stats-feed yellow
  count (`yellow_cards_*`, copied into `yellow_*`) is NEVER the
  target; it is retained for provenance only. This target decision
  is frozen here, before fitting. Primary line **4.5** (dev-period
  over-rate 0.472, closest to 0.5; the 3.5 over-rate is 0.642).
  Ladder 3.5/4.5/5.5 reported.
- Arms: **Gate Zero only** (reference unmodified; referee not
  used). X8 is NOT an arm: referee strictness reliability is
  r = 0.178 pooled and season-unstable (0.658 / 0.368 / −0.398 /
  0.205 / 0.025), and referee coverage is 40.0% in 2021/2022 and
  70.4% in the virgin — below the programme's arm standard.
  Recorded in FEATURES; not built.
- Training seed 2021/2022; dev 2022/2023–2024/2025 (n = 720);
  dev harness must not read 2025/2026 / 2026/2027 rows.
- Baselines: league base rate; naive trailing-10 through the same
  count distribution as the reference harness.
- Virgin: 2025/2026 (n = 240), read ONCE, only if Gate Zero passes
  the dev gate. Calibration at 4.5 = actual − mean predicted,
  SE = sd(y_i − p_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@4.5 beats BOTH baselines (league base rate; naive trailing-10), else the candidate is dead, no virgin read. Virgin legs — (i) LL@4.5 ≤ best baseline's; (ii) calibration |actual − mean P(over 4.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS. If Gate Zero passes all legs it ships; if any leg fails, K-RU verdict is FAIL and nothing ships.

Mechanical reading: Gate Zero passes iff it survives the dev gate
AND passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as
such). Gate Zero dev failure ⇒ FAIL, virgin NOT read.

## Outputs

Engine `engine/cards/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/k_ru_virgin_predictions.csv` (FT ladder 3.5/4.5/5.5;
1H/2H presentation-only via frozen yellows constant 0.3519, lines
1H 0.5/1.5/2.5, 2H 1.5/2.5/3.5). Verdict `reports/K_RU_VERDICT.md`.
