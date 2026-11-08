# Pre-registration — S-BG (Bulgaria First Professional League SOT model)

Frozen: 2026-11-10, before any fitting. Branch `build/bg-first`.
Design authority: `analysis/MODEL_DESIGN.md` (S-BG); features X5
(FEATURES.md; SOT reliability for 0.746 / against 0.645). Reference:
production `model_sot.py` v5 pattern; sibling analogue
`league/ZA-PSL/prereg/PREREG_S_ZA.md` — the shared engine is carried
over in form, changing only league, seasons, lines and the halves
decision below.
Phase rule (frozen): all phases in every window, flagged; no phase
feature. Team identity is the FotMob team id.
Calibration = **actual − predicted** everywhere in this build.

- Target: total SOT (stats feed). Primary line **8.5**
  (scored-dev over-rate 0.458, closest to 0.5). Ladder 7.5 / 8.5 /
  9.5 reported, gate at 8.5.
- Arms: **Gate Zero** (v5 unmodified: joint Poisson regression +
  Negative Binomial r = 79.94 + Beta-Binomial on-target ratio with
  prior P = 200, ensemble with naive trailing-10, constants as the
  TH/ZA SOT preregs); **RS** — identical, ratio prior P = 20,000.
  X4/X6 do not exist here (no shotmap) and are not arms.
- Training warm-up 2021/2022 (stats rows n = 216, updates state,
  never scored); dev evaluation 2022/2023–2024/2025 (stats rows
  n = 841) per-match walk-forward (predict-then-update, date order).
  Dev harness must not read 2025/2026 / 2026/2027 rows.
- Baselines: league base rate (pooled pre-season over-rate at each
  line) and naive trailing-10 through the same NB.
- Virgin: 2025/2026 (stats rows n = 293), read ONCE, only for arms
  passing the dev gate. Calibration at 8.5 = actual − mean
  predicted, SE = sd(y_i − p_i)/√n.
- Halves: **FT-only** — no period splits and no event source for SOT
  exist in this league (frozen; halves constant null in config).

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@8.5 beats BOTH baselines (league base rate; naive trailing-10), else the arm is dead, no virgin read. Virgin legs — (i) LL@8.5 ≤ Gate Zero's AND ≤ best baseline's (Gate Zero: ≤ best baseline's); (ii) calibration |actual − mean P(over 8.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass (variant dev LL@8.5 ≤ Gate Zero's in ≥2 of 3 dev seasons). Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such)
AND, for the variant, leg (iii). Ties → simpler arm (Gate Zero
before RS). Gate Zero dev failure ⇒ variants moot, FAIL, virgin
NOT read.

## Outputs

Engine `engine/sot/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/s_bg_virgin_predictions.csv` (FT ladder 7.5/8.5/9.5
only — no halves columns, FT-only market). Verdict
`reports/S_BG_VERDICT.md`.
