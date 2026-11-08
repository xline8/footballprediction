# Pre-registration — S-FR (FR-Ligue2 shots-on-target model)

Frozen: 2026-11-09, before any fitting. Branch `build/fr-ligue2`.
Design authority: `analysis/MODEL_DESIGN.md` (S-FR); features X5
base (FEATURES.md); evidence EDA. Reference: production
`model_sot.py` v5; ES analogue `PREREG_S_ES.md` — the v5 architecture
constants there are carried over verbatim (ridge lambda = 100,
HL = 365, lazy refit 7 days, total-shots ratings prior K = 8,
Beta-Binomial prior P = 200, ensemble 50/50 with naive trailing-10,
NB size r = 79.94 frozen). X4 (xG/shot) and X6 (xGOT) are NOT arms:
both are era-dead in this league (shotmap exists in 0–1.6% of dev
matches; the era starts in the virgin). The count target itself is
stats-feed and era-free.

- Target: total SOT = `ShotsOnTarget_home + ShotsOnTarget_away`
  (stats feed, ~100% of matches every season). Primary line **8.5**
  (dev over-rate 0.437, closest to 0.5; 7.5 → 0.566). Ladder
  7.5 / 8.5 / 9.5 reported, gate at 8.5.
- Arms: **Gate Zero** (v5 unmodified); **RS** (Gate Zero with the
  BB prior raised P = 200 → 20,000). Team state keyed on team_id.
- Walk-forward: per-match, chronological (date, match_id),
  predict-then-update, date-grouped (same-date matches never see
  each other). Warm-up: 2021/2022 updates state, never scored.
- Dev: scored seasons 2022/2023–2024/2025 (n = 1,065). The dev
  harness must not read 2025/2026 or 2026/2027 rows at all.
- Baselines: league base rate (prior-seasons over-8.5 rate, constant
  within target season); naive trailing-10 through the same NB.
- Virgin: 2025/2026 (n = 306), read ONCE, only for dev-passing arms,
  continuing from the dev end state. Calibration = actual rate −
  mean P(over 8.5) (this league's convention), SE = sd(y_i − p_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@8.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@8.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |actual − mean P(over 8.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts) AND, for variants,
leg (iii) — variant dev LL@8.5 ≤ Gate Zero's in at least half of the
dev seasons (≥2 of 3). Ties → simpler arm (Gate Zero, RS). If
Gate Zero fails its dev gate, variants are moot, verdict FAIL,
virgin NOT read.

## Outputs

Engine `engine/sot/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/s_fr_virgin_predictions.csv` (shipped arm; FT ladder
7.5/8.5/9.5 ensemble probabilities; 1H/2H ladders presentation-only
via frozen SOT constant 0.4738, NB r = 79.94, lines 1H 2.5/3.5/4.5,
2H 3.5/4.5/5.5). Verdict `reports/S_FR_VERDICT.md`.
