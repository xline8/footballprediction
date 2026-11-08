# Pre-registration — S-EG (EG-PremierLeague shots-on-target model)

Frozen: 2026-11-09, before any fitting. Branch `build/eg-premier`.
Design authority: `analysis/MODEL_DESIGN.md` (S-EG); features X5
base (FEATURES.md); evidence EDA F1/F2/F5. Reference: production
`model_sot.py` v5; SA analogue `league/SA-ProLeague/prereg/PREREG_S_SA.md`
— the v5 architecture constants there are carried over verbatim
(ridge lambda = 100, HL = 365, lazy refit 7 days, total-shots
ratings prior K = 8, Beta-Binomial prior P = 200, ensemble 50/50
with naive trailing-10, NB size r = 79.94 frozen). X4 and X6 are
NOT arms: shotmap/xG exist only from the virgin season 2025/2026,
so neither can be dev-validated (FEATURES: dropped).
Phase rule (frozen, MODEL_DESIGN): all phases are ordinary rows in
every window; no phase feature anywhere.

- Target: total SOT = `ShotsOnTarget_home + ShotsOnTarget_away`
  (stats feed). Primary line **6.5** (scored-dev pooled
  2022/2023–2024/2025 over-rate 0.551, closest to 0.5). Ladder
  5.5 / 6.5 / 7.5 reported, gate at 6.5.
- Arms: **Gate Zero** (v5 unmodified); **RS** (Gate Zero with the
  BB prior raised P = 200 → 20,000). No other arms.
- Walk-forward: per-match, chronological (date, match_id),
  predict-then-update, date-grouped (same-date matches never see
  each other). Warm-up: 2021/2022 updates state, never scored.
- Dev: scored seasons 2022/2023–2024/2025 (rows with the target
  present; n = 826 of 837). The dev harness must not read
  2025/2026 or 2026/2027 rows at all.
- Baselines: league base rate (prior-seasons over-6.5 rate,
  constant within target season); naive trailing-10 through the
  same NB.
- Virgin: 2025/2026 (n = 322), read ONCE, only for dev-passing
  arms, continuing from the dev end state. Calibration = actual
  over-6.5 rate − mean P(over 6.5), SE = sd(y_i − p_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@6.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@6.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |actual − mean P(over 6.5)| ≤ 1.0pp is clean PASS; beyond 1 SE is FAIL, with SE reported, a breach within 1 SE of the 1.0pp boundary is PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts) AND, for variants,
leg (iii) — variant dev LL@6.5 ≤ Gate Zero's in at least 2 of the 3
dev seasons. Ties → simpler arm (Gate Zero before RS). If Gate
Zero fails its dev gate, variants are moot, verdict FAIL, virgin
NOT read.

## Outputs

Engine `engine/sot/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/s_eg_virgin_predictions.csv` (shipped arm; FT ladder
5.5/6.5/7.5 ensemble probabilities; 1H/2H ladders presentation-only
via frozen SOT constant 0.4445, NB r = 79.94, lines 1H 2.5/3.5/4.5,
2H 3.5/4.5/5.5). Verdict `reports/S_EG_VERDICT.md`.
