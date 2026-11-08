# Pre-registration — S-CH (CH-SuperLeague shots-on-target model)

Frozen: 2026-11-09, before any fitting. Branch `build/ch-superleague`.
Design authority: `analysis/MODEL_DESIGN.md` (S-CH); features X5
base (FEATURES.md); evidence F2/F6. Reference:
production `model_sot.py` v5; J1 analogue `PREREG_S_J1.md` — the v5
architecture constants there are carried over verbatim (ridge
lambda = 100, HL = 365, lazy refit 7 days, total-shots ratings
prior K = 8, Beta-Binomial prior P = 200, ensemble 50/50 with naive
trailing-10, NB size r = 79.94 frozen). X6 (xGOT) is NOT an arm:
its CH reliability check failed (EDA F7, r = 0.212).

- Target: total SOT = `ShotsOnTarget_home + ShotsOnTarget_away`
  (stats feed). Primary line **9.5** (dev over-rate 0.463, closest
  to 0.5). Ladder 8.5 / 9.5 / 10.5 reported, gate at 9.5.
- Arms: **Gate Zero** (v5 unmodified); **RS** (Gate Zero with the
  BB prior raised P = 200 → 20,000). **No X4 arm**: the xG/shot
  reliability check failed the arm standard in CH (EDA F6,
  r = 0.247 vs DK's adopted 0.348); no X6 arm (F7).
- Walk-forward: per-match, chronological (date, match_id),
  predict-then-update, date-grouped (same-date matches never see
  each other). Warm-up: 2021/2022 updates state, never scored.
- Dev: scored seasons 2022/2023–2024/2025 (n = 636). The dev
  harness must not read 2025/2026 or 2026/2027 rows at all.
- Baselines: league base rate (prior-seasons over-9.5 rate, constant
  within target season); naive trailing-10 through the same NB.
- Virgin: 2025/2026 (n = 228), read ONCE, only for dev-passing arms,
  continuing from the dev end state. Calibration = mean P(over 9.5)
  − actual rate, SE = sd(p_i − y_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@9.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@9.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over 9.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts) AND, for variants,
leg (iii) — variant dev LL@9.5 ≤ Gate Zero's in at least half of the
dev seasons (≥2 of 3). Ties → simpler arm (Gate Zero before RS). If
Gate Zero fails its dev gate, variants are moot, verdict FAIL,
virgin NOT read.

## Outputs

Engine `engine/sot/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/s_ch_virgin_predictions.csv` (shipped arm; FT ladder
8.5/9.5/10.5 ensemble probabilities; 1H/2H ladders presentation-only
via frozen SOT constant 0.453, NB r = 79.94, lines 1H 3.5/4.5/5.5,
2H 4.5/5.5/6.5). Verdict `reports/S_CH_VERDICT.md`.
