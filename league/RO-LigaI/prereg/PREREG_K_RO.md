# Pre-registration — K-RO (RO-LigaI cards model)

Frozen: 2026-11-10, before any fitting. Branch `build/ro-ligai`.
Design authority: `analysis/MODEL_DESIGN.md` (K-RO); features X5,
X8; evidence F1/F2/F8/F12. Reference: production `model_cards.py`;
CH analogue `PREREG_K_CH.md` and the J1 K engine — the architecture
(team yellow ratings + count distribution + naive ensemble
structure of the reference) is carried over in form; the shared
constants are mirrored, changing only league, seasons, line, the
target source below, and the X8 shrinkage.

- Target: **event-unified yellows** = `yellow_home + yellow_away`
  from matchFacts card events (`card == "Yellow"`), all eras
  (PREPROCESSING — the stats feed exists only 2025/2026+ and
  undercounts the events by ≈0.21/match where both exist; the
  artefact is measured in EDA F12). Primary line **4.5**
  (dev over-rate 0.467, closest to 0.5). Ladder 3.5/4.5/5.5.
- Arms: **Gate Zero** (reference unmodified; referee not used);
  **X8** — Gate Zero plus the referee covariate: appointed
  referee's trailing in-league mean yellows/match (strictly
  pre-match), shrunk toward the league mean with prior weight
  8 matches; referees with <8 prior in-league matches take the
  shrunk league mean; the covariate enters exactly as in the J1
  K engine's referee arm. Operational condition (inherited): if a
  fixture's appointment is not published pre-match in the live
  pipeline, it falls back to Gate Zero — no imputation. Warehouse
  coverage is 99.4% overall and ≥99.4% in every complete season,
  so the arm is testable across the whole dev window.
- Training seed 2021/2022; dev 2022/2023–2024/2025 (n = 945);
  dev harness must not read 2025/2026 / 2026/2027 rows.
- Baselines: league base rate; naive trailing-10 through the same
  count distribution as the reference harness.
- Virgin: 2025/2026 (n = 315), read ONCE, only for dev-passing arms.
  Calibration at 4.5, SE = sd(p_i − y_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@4.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@4.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over 4.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading as in PREREG_S_RO (variant sign check ≥2 of 3;
ties → Gate Zero; Gate Zero dev failure ⇒ FAIL, virgin NOT read).

## Outputs

Engine `engine/cards/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/k_ro_virgin_predictions.csv` (FT ladder 3.5/4.5/5.5;
1H/2H presentation-only via frozen yellows constant 0.330, lines
1H 0.5/1.5/2.5, 2H 1.5/2.5/3.5). Verdict `reports/K_RO_VERDICT.md`.
