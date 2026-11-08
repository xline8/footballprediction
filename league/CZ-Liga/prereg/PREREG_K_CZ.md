# Pre-registration — K-CZ (CZ-Liga cards model)

Frozen: 2026-11-10, before any fitting. Branch `build/cz-liga`.
Design authority: `analysis/MODEL_DESIGN.md` (K-CZ); features X5;
evidence F1/F2/F5/F6. Reference: production `model_cards.py`;
RO analogue `PREREG_K_RO.md` and the J1 K engine — the architecture
(team yellow ratings + count distribution + naive ensemble
structure of the reference) is carried over in form; the shared
constants are mirrored, changing only league, seasons, line, and
the target source below. The X8 referee arm of the RO/J1 preregs is
NOT registered here: referee names are absent from every dev-era
payload in this league (FEATURES X8, EDA F5), so the arm cannot be
dev-tested; no replacement variant is invented.

- Target: **event-unified yellows** = `yellow_home + yellow_away`
  from matchFacts card events (`card == "Yellow"`), all eras
  (PREPROCESSING — the stats feed's yellow keys exist only
  2025/2026+ and differ from the events by ≈+0.10/match where both
  exist; the artefact is measured in EDA F6). Primary line **3.5**
  (dev over-rate 0.5676, closest to 0.5). Ladder 2.5/3.5/4.5.
- Arms: **Gate Zero only** (reference unmodified; referee not used).
- Training seed 2021/2022; dev 2022/2023–2024/2025 (n = 810; the
  event target exists for every included match). Dev harness must
  not read 2025/2026 / 2026/2027 rows.
- Baselines: league base rate; naive trailing-10 through the same
  count distribution as the reference harness.
- Virgin: 2025/2026 (n = 270), read ONCE, only if Gate Zero passes
  the dev gate. Calibration at 3.5, SE = sd(p_i − y_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@3.5 beats BOTH baselines (league base rate; naive trailing-10), else the candidate is dead, no virgin read. Virgin legs — (i) LL@3.5 ≤ best baseline's; (ii) calibration |mean P(over 3.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS. If Gate Zero passes all legs it ships; if none passes, K-CZ verdict is FAIL and nothing ships.

(Single-arm candidate: the both-pass rule and leg (iii) of the
multi-arm preregs do not apply. Gate Zero dev failure ⇒ FAIL,
virgin NOT read.)

## Outputs

Engine `engine/cards/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/k_cz_virgin_predictions.csv` (FT ladder 2.5/3.5/4.5;
1H/2H presentation-only via frozen yellows constant 0.3150, lines
1H 0.5/1.5/2.5, 2H 1.5/2.5/3.5). Verdict `reports/K_CZ_VERDICT.md`.
