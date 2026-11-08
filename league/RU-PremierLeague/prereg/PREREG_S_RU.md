# Pre-registration — S-RU (RU-Premier League shots-on-target model)

Frozen: 2026-11-10, before any fitting. Branch `build/ru-premier`.
Design authority: `analysis/MODEL_DESIGN.md` (S-RU); features X5
base (FEATURES.md); evidence EDA reliabilities (SOT for 0.849 /
against 0.846). Reference: production `model_sot.py` v5; PL analogue
`PREREG_S_PL.md` — the v5 architecture constants there are carried
over verbatim (ridge lambda = 100, HL = 365, lazy refit 7 days,
total-shots ratings prior K = 8, Beta-Binomial prior P = 200,
ensemble 50/50 with naive trailing-10, NB size r = 79.94 frozen).
X4 is NOT an arm: RU shotmap xG/shot exists only from the virgin
season and cannot be dev-gated. X6 (xGOT) is NOT an arm: same
virgin-era bar.
Phase rule (frozen, MODEL_DESIGN): all rows are phase `regular`;
no phase feature anywhere.
Calibration = **actual − predicted** everywhere in this build.

- Target: total SOT = `ShotsOnTarget_home + ShotsOnTarget_away`
  (stats feed). Primary line **8.5** (dev-period over-rate 0.537,
  closest to 0.5; the 9.5 over-rate is 0.411). Ladder 7.5 / 8.5 / 9.5
  reported, gate at 8.5.
- Arms: **Gate Zero** (v5 unmodified); **RS** (Gate Zero with the
  BB prior raised P = 200 → 20,000).
- Walk-forward: per-match, chronological (date, match_id),
  predict-then-update, date-grouped (same-date matches never see
  each other). Warm-up: 2021/2022 updates state, never scored.
- Dev: scored seasons 2022/2023–2024/2025 (n = 720). The dev
  harness must not read 2025/2026 or 2026/2027 rows at all.
- Baselines: league base rate (prior-seasons over-8.5 rate, constant
  within target season); naive trailing-10 through the same NB.
- Virgin: 2025/2026 (n = 240), read ONCE, only for dev-passing arms,
  continuing from the dev end state. Calibration = actual rate −
  mean P(over 8.5), SE = sd(y_i − p_i)/√n.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@8.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@8.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |actual − mean P(over 8.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts) AND, for variants,
leg (iii) — variant dev LL@8.5 ≤ Gate Zero's in at least half of the
dev seasons (≥2 of 3). Ties → simpler arm (Gate Zero before RS).
If Gate Zero fails its dev gate, variants are moot, verdict FAIL,
virgin NOT read.

## Outputs

Engine `engine/sot/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/s_ru_virgin_predictions.csv` (shipped arm; FT ladder
7.5/8.5/9.5 ensemble probabilities; 1H/2H ladders presentation-only
via frozen SOT constant 0.4612, NB r = 79.94, lines 1H 3.5/4.5/5.5,
2H 4.5/5.5/6.5). Verdict `reports/S_RU_VERDICT.md`.
