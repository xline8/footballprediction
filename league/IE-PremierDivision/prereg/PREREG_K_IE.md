# Pre-registration — K-IE (Ireland Premier Division cards model)

Frozen: 2026-11-10, before any fitting. Branch `build/ie-premier`.
Design authority: `analysis/MODEL_DESIGN.md` (K-IE); features X5;
evidence F1/F2/F8. Reference: production `model_cards.py`; SCO
analogue `PREREG_K_SCO.md` and the J1 cards engine form (team yellow
ratings + count distribution + naive ensemble structure of the
reference) — carried over in form, changing only league, seasons,
line, and the target provenance below.

- Target: **event-unified yellows** = `yellow_home + yellow_away`
  in `ie_matches.csv`, where yellow_* counts match events of type
  Card with card ∈ {Yellow, YellowRed} attributed by isHome
  (`cards_source = 'events'` for all rows). The stats-feed
  `yellow_cards` is NOT the target: it disagrees with the event
  count in 18.3% of the 717 dev matches that carry it, including
  matches where the stats feed reports 0–0 against 8 event cards
  (artefact verified in DATA_UNDERSTANDING / EDA; the same
  stats-vs-events artefact seen in 9 earlier leagues). Primary
  line **4.5** (dev over-rate 0.546, closest to 0.5). Ladder
  3.5/4.5/5.5 reported, gate at 4.5.
- Arms: **Gate Zero only** (reference unmodified; referee not
  used). The X8 referee arm is NOT built: its IE reliability check
  failed (EDA F8, split-half r = 0.239 on event yellows, below the
  frozen 0.40 adoption threshold), and named-referee coverage is
  0% in 2021 and 22.2% in 2022 in any case.
- Training seed 2021 (event target + referee exist for all 2021
  matches even though the stats feed does not); dev evaluation
  2022–2025 (n = 720); dev harness must not read 2026 rows.
- Baselines: league base rate; naive trailing-10 through the same
  count distribution as the reference harness.
- Virgin: 2026 (n = 180, complete), read ONCE, only if Gate Zero
  passes the dev gate. Calibration at 4.5, SE = sd(p_i − y_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@4.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@4.5 ≤ best baseline's (single-arm candidate: the Gate Zero comparator leg is vacuous); (ii) calibration |mean P(over 4.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS. Both-pass rule is vacuous (one arm): Gate Zero passes ⇒ it ships; it fails any leg ⇒ FAIL, nothing ships.

## Outputs

Engine `engine/cards/`; `results_dev.json` (+ per-match CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/k_ie_virgin_predictions.csv` (FT ladder 3.5/4.5/5.5;
1H/2H presentation-only via frozen yellows constant 0.3238, lines
1H 0.5/1.5/2.5, 2H 2.5/3.5/4.5). Verdict `reports/K_IE_VERDICT.md`.
