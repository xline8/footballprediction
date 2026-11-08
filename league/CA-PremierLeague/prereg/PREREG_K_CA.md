# Pre-registration — K-CA (CA-PremierLeague cards model)

Frozen: 2026-11-10, before any fitting. Branch `build/ca-premier`.
Design authority: `analysis/MODEL_DESIGN.md` (K-CA); features X5;
evidence per `analysis/EDA.md` (cards artefact audit). Reference:
production `model_cards.py`; SK analogue `PREREG_K_SK.md` — the
architecture (team yellow ratings + count distribution + naive
ensemble structure of the reference) is carried over in form. The
X8 referee arm is NOT registered: referee coverage collapses in
the virgin season (40/117 payloads named in 2025 vs 110/117 in
2024; FEATURES X8), so the arm cannot be virgin-tested; no
replacement variant is invented.

## Target — decided from this league's artefact audit, frozen here

- **Target: stats-feed yellows** = `yellow_cards_home +
  yellow_cards_away` (stats `Periods.All`), **era-restricted to
  2023 onward**. Reason, from the audit (EDA): the stats yellow
  series is a feed artefact in 2021/22 — 82/115 (2021) and 89/117
  (2022) matches record a stats total of exactly 0, season means
  1.15/0.94 against 4.35 (2023), 4.99 (2024), 4.71 (2025) — while
  the event feed carries NO "Yellow" card events at all before
  2025 (only Red/YellowRed), so an event-yellow target cannot be
  constructed for any dev-era season. From 2023 the stats series
  is credible (zero totals: 4/117 in 2023, 0/117 in 2024 and
  2025), and in 2025, the one season where both sources exist,
  events vs stats agree exactly on 90/112 regular matches with
  means 4.94 (events) vs 4.71 (stats) — no material artefact in
  the adopted era. The 2021/22 stats zeros are a feed failure,
  not a low-card era, and those seasons are excluded from every
  cards window below.
- Primary line **4.5** (credible-era pooled over-rate 0.549107
  vs 3.5 → 0.723214; 4.5 is closest to 0.5). Ladder 3.5/4.5/5.5.
- Arms: **Gate Zero only** (reference unmodified; referee not used).
- Warm-up seed 2023 (never scored); dev 2024 only (n = 112; the
  event target does not exist and the stats target is not
  credible before 2023, so no earlier dev season is legitimate —
  the thin dev window is reported as such, not widened). Dev
  harness must not read 2025 / 2026 rows.
- Baselines: league base rate (2023 over-4.5 rate); naive
  trailing-10 through the same count distribution as the
  reference harness.
- Virgin: 2025 (n = 112), read ONCE, only if Gate Zero passes
  the dev gate. Calibration at 4.5, SE = sd(p_i − y_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@4.5 beats BOTH baselines (league base rate; naive trailing-10), else the candidate is dead, no virgin read. Virgin legs — (i) LL@4.5 ≤ best baseline's; (ii) calibration |mean P(over 4.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS. If Gate Zero passes all legs it ships; if none passes, K-CA verdict is FAIL and nothing ships.

(Single-arm candidate: the both-pass rule and leg (iii) of the
multi-arm preregs do not apply. Gate Zero dev failure ⇒ FAIL,
virgin NOT read.)

## Outputs

Engine `engine/cards/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/k_ca_virgin_predictions.csv` (FT ladder 3.5/4.5/5.5;
1H/2H presentation-only via frozen yellows constant 0.314532,
lines 1H 0.5/1.5/2.5, 2H 1.5/2.5/3.5). Verdict
`reports/K_CA_VERDICT.md`.
