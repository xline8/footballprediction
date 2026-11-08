# Verdict — K-CR (Costa Rica Primera Division cards model)

**Verdict: FAIL — virgin calibration leg. Nothing ships.**

Prereg: `league/CR-PrimeraDivision/prereg/PREREG_K_CR.md` (frozen 2026-11-10, before any fitting).
Engine: `league/CR-PrimeraDivision/engine/cards/`. Results: `engine/cards/results_dev.json` (+ CSV),
`engine/cards/results_virgin.json`. Predictions (record only, labelled not-shipped):
`league/CR-PrimeraDivision/predictions/k_cr_virgin_predictions.csv` (262 rows, Gate Zero).
Single arm: Gate Zero (unmodified production `model_cards.py` pattern, yellows only, no referee arm —
referee identity is absent in this league, EDA F6).

## Dev results (2023/2024 regular; Apertura warm-up, Clausura scored)

| Split | n | | LL@4.5 model | LL@4.5 base | LL@4.5 naive | r model / base / naive |
|---|---|---|---|---|---|---|
| Clausura 2023/2024 (scored) | 132 | | **0.64779** | 0.64963 | 0.65911 | 13.55 / 11.89 / 10.44 |

- Dev gate: pooled dev LL@4.5 beats both baselines — **PASS**, but thin: +0.0018 vs the base rate.
  At the secondary lines the model LOSES to base on dev (LL@3.5: 0.7118 vs 0.7046; LL@5.5: 0.5284
  vs 0.5058). The scored Clausura was a low-cards half (actual over-4.5 rate 34.8%, mean_p 37.7%).
- Dev gate passed, so the virgin window was read once, as pre-registered.

## Virgin results (2024/2025 regular, n = 262; fit on 2023/2024 only; r re-estimated on 2023/2024)

| Line | LL model | LL base | LL naive | Mean P(model) | Actual over-rate |
|---|---|---|---|---|---|
| **4.5 (primary)** | **0.68706** | 0.69545 | 0.69602 | 0.386 | 0.443 |
| 3.5 | 0.66948 | 0.67429 | — | 0.550 | 0.622 |
| 5.5 | 0.57104 | 0.58994 | — | 0.253 | 0.271 |

Virgin r: model 11.56, base 11.01, naive 8.85.

## Gate arithmetic (mechanical, per prereg)

- Virgin LL leg (i): 0.68706 ≤ 0.69545 (best baseline) — **PASS**.
- Virgin calibration leg (ii) at 4.5: mean P(over 4.5) − actual = **−0.0564 (−5.64pp)**,
  SE = 0.0305. |diff| = 5.64pp > 1.0pp, and the breach beyond the boundary (4.64pp) exceeds 1 SE
  (3.05pp) — **FAIL** (not a provisional pass).
- Sign check (iii): vacuous for a single-arm candidate (recorded N/A per prereg).

The calibration leg is a hard leg. K-CR verdict is FAIL and nothing ships.

## Diagnosis

A level drift the decayed model lags. Yellows per match rise across eras on the reliable feed:
4.00 (2023/24) → 4.19 (2024/25) → 5.36 (2025/26). The model, fitted on 2023/24, prices the old
level: on virgin it expects P(over 4.5) = 0.386 against an actual 0.443, and the same under-prediction
appears at 3.5 (0.550 vs 0.622). The ranking is better than base rate (the model wins LL at all three
lines on virgin), but its level is biased low by ~5–7pp — exactly what the calibration leg is designed
to catch. The dev pass was already thin (+0.0018 vs base at 4.5, losing at both secondary lines), so
the virgin failure is consistent with a model that barely beats the base rate rather than a surprise.

## Verification

An independent second-path reimplementation of the prereg spec (fresh code, no reuse of
`engine/cards/model.py` or `harness.py`) reproduces the harness numbers to 6 decimals: dev LL@4.5
0.647790 / 0.649633 / 0.659111, virgin LL@4.5 0.687062 / 0.695450 / 0.696022, calibration diff
−0.056436, SE 0.030511, r values identical.

## Operational referee check (required by prereg)

- (a) Referee-identity coverage: **0 known of 262 virgin matches** (2024/2025); 0 in 5 of 6 seasons
  overall (only 22/192 known in 2025/2026). The predictions file records `referee_known = False`
  for every virgin row.
- (b) Historical (completed-match) records are post-match snapshots with no publication timestamp;
  they cannot by themselves prove an appointment was public before kickoff. Even the 22 known 2025/26
  referees prove nothing about pre-match availability.
- (c) Operating rule shipped: there is no referee arm, so no fallback is needed — the question is moot
  for this league. Any future referee arm would require both identity coverage and a pre-match
  publication check first.

## What ships

Nothing. K-CR does not ship. The predictions file is retained for the record (Gate Zero, labelled
not-shipped in this verdict) and must not be presented as a live product.
