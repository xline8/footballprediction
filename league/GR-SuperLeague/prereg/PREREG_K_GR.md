# Pre-registration — K-GR (GR-SuperLeague cards model)

Frozen: 2026-11-09, before any fitting. Branch `build/gr-super`.
Design authority: `analysis/MODEL_DESIGN.md` (K-GR); features X5
only; evidence EDA (yellows for 0.686 / against 0.488; referee
split-half r = 0.262 — X8 DROPPED at design, see FEATURES).
Reference: production `model_cards.py`; PL analogue
`PREREG_K_PL.md` and the J1 K engine (`league/J1/engine/cards/`) —
the architecture (team yellow ratings + count distribution + naive
ensemble structure of the reference) is carried over in form;
mirror the shared constants, changing only league, seasons and
line.
Phase rule (frozen, MODEL_DESIGN): all phases are ordinary rows;
no phase feature anywhere.
Calibration = **actual − predicted** everywhere in this build.

- Target: unified yellows = `yellow_home + yellow_away` (stats feed
  for 1,017 matches, `cards_source='events'` for the 244 matches
  where the stats feed carries no yellow_cards key — 239 of the
  240 matches of 2021/2022 plus 5 in 2024/2025; the stats-vs-events check on the 1,017
  dual-source matches: exact agreement 81.4%, stats lower in 15.7%,
  higher in 2.9%, mean stats − events = −0.250 — the artefact shape
  seen across the programme; the unified target stands as built).
  Primary line **4.5** (dev-period over-rate 0.520, closest to 0.5;
  the 3.5 over-rate is 0.699). Ladder 3.5/4.5/5.5 reported.
- Arms: **Gate Zero ONLY** (reference unmodified; referee not
  used). There is no X8 arm in this build: referee reliability
  0.262 over the 15 qualifying referees (117 distinct named, heavy
  foreign rotation; coordinator random re-split −0.07) fails the
  programme's referee standard (lowest adopted anywhere: BE 0.378),
  and seed-season referee coverage is 0.0%. This is a design-stage
  drop, recorded before any fitting — not a post-hoc removal.
- Training seed 2021/2022; dev 2022/2023–2024/2025 (n = 716);
  dev harness must not read 2025/2026 / 2026/2027 rows.
- Baselines: league base rate; naive trailing-10 through the same
  count distribution as the reference harness.
- Virgin: 2025/2026 (n = 236), read ONCE, only if Gate Zero passes
  dev. Calibration at 4.5 = actual − mean predicted, SE = sd(y_i − p_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@4.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@4.5 ≤ best baseline's; (ii) calibration |actual − mean P(over 4.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS. Both-pass rule does not apply (single arm): Gate Zero passes both virgin legs → ships; any leg fails → FAIL, nothing ships.

Mechanical reading: Gate Zero dev failure ⇒ FAIL, virgin NOT read.

## Outputs

Engine `engine/cards/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/k_gr_virgin_predictions.csv` (FT ladder 3.5/4.5/5.5;
1H/2H presentation-only via frozen yellows constant 0.3522, lines
1H 1.5/2.5/3.5, 2H 2.5/3.5/4.5). Verdict `reports/K_GR_VERDICT.md`.
