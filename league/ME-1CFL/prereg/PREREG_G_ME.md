# Pre-registration — G-ME (Montenegro 1. CFL goals)

Frozen: 2026-11-10, before any fitting. Design authority:
`analysis/MODEL_DESIGN.md`; data decisions: `analysis/FEATURES.md`;
evidence: `analysis/EDA.md` (F1/F2/F3/F4/F5). Target: goals,
primary OU2.5, with home-win calibration legs. Dev scored n = 539
(2022/2023–2024/2025); training seed 2021/2022 (n=179 played);
virgin 2025/2026 (n = 180, complete); confirmatory 2026/2027
reserved (in progress, not in the warehouse complete). All seasons
are a single round-robin phase (10 teams x 36 rounds); 2021/2022
played n=179 (one round-36 fixture never started, excluded) and
2024/2025 n=179 (one round-36 fixture absent from the index).
Calibration = actual − predicted. The dev primary over-rate is
0.4453 at OU2.5 (dev-scored window 2022/2023–2024/2025, n = 539;
OU1.5 0.7013, OU3.5 0.2412).

## Reference architecture (all arms share this unless an arm says otherwise)

- Dixon-Coles fit, copied pattern from production `model_v2.py`
  via the sibling G-LT implementation (`league/LT-Toplyga/engine/
  goals/dc.py`): iterative multiplicative updates, 14 sweeps,
  damping 0.7, +0.25 smoothing, home advantage `h` fitted (init
  0.28), attack `a` and defence `d` per team (init 0), score matrix
  to MAXG = 10 with the production `tau` low-score correction.
- Rho: chosen per fit from the grid (0.0, −0.05, −0.10, −0.15) by
  weighted log-likelihood on goals only, exactly as production.
- Observation: goals only (no xG exists in this league — the
  reference blend's documented fallback; FEATURES X1).
- Time decay: weight w = 0.5 ** ((cutoff − match_date).days / 270).
  Half-life 270 days is the production value, frozen — no search.
- Fit scope for a target season S: all ME-1CFL played matches with
  date strictly before the first match date of S (expanding window,
  season-blocked: one fit per target season, whole season predicted
  from that fit).
- Teams unseen in training start at the league mean (a = d = 0).

## Arms

1. **Gate Zero** — the unmodified reference above. New teams start
   at the league mean.
2. **Arm SHRINK** — Gate Zero plus the G-J2 post-mortem shrinkage:
   a team's attack/defence ratings are multiplied by
   `min(1.0, counts / 6.0)` where counts = its matches in the
   training window. Thin-data teams at season starts in this
   league (EDA F5): 2022/2023: 2, 2023/2024: 1, 2024/2025: 2,
   2025/2026: 0, 2026/2027: 0. The thin teams are brand-new ids
   with 0 training matches, so SHRINK is expected to coincide
   with Gate Zero (as in G-LT); run anyway and gated like any arm.

There is NO X2 arm: no Montenegrin sibling league exists in the
warehouse, so no cross-tier mover prior can be measured (EDA F4,
FEATURES X2 DROPPED). New ids enter at the league mean in every
arm. No other arms exist; post-hoc arms are forbidden.

## Dev protocol

- Dev period: seed 2021/2022; evaluation seasons 2022/2023,
  2023/2024, 2024/2025 under the expanding season-blocked
  walk-forward above. Pooled dev = the three evaluation seasons
  combined (n = 539).
- Metrics per arm per season and pooled: mean 1X2 log-loss
  (natural log), mean RPS (outcomes ordered H, D, A;
  RPS = 0.5 · Σ_k (Σ_{j≤k} p_j − Σ_{j≤k} y_j)²), mean OU2.5
  log-loss (binary, on P(over 2.5)).
- Baselines: climatology — for target season S, the pooled outcome
  rates (home win / draw / away win) and OU2.5 over-rate of all
  ME-1CFL seasons strictly before S. The same climatology
  probabilities score LL, RPS and OU LL for that season.
- The dev harness must not read season "2025/2026" or "2026/2027"
  rows at all. Virgin data is touched only by the separate virgin
  step, once, after dev results are frozen in the results file.

## Virgin protocol

- Virgin window: season "2025/2026" (n = 180, complete). Fit = all
  ME-1CFL played matches dated before the first 2025/2026 match
  (seasons 2021/2022–2024/2025). Read ONCE, after dev freezes.
- Virgin climatology: pooled 2021/2022–2024/2025 outcome rates and
  OU2.5 over-rate.
- Calibration per arm: (i) mean predicted home-win probability
  minus actual home-win rate; (ii) mean predicted P(over 2.5)
  minus actual over-rate. Standard error of each difference:
  SE = sd(pred_i − y_i) / √n over the 180 matches, reported with
  the difference. Calibration is actual minus predicted.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat
climatology, and OU2.5 LL must beat the base-rate baseline, else
the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤
Gate Zero's AND ≤ climatology's; (ii) calibration leg: |actual −
mean predicted| ≤ 1.0pp pooled for home-win rate and for OU2.5
over-rate, SEs reported; a breach within 1 SE of the boundary is
recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign
check on dev (arm LL ≤ Gate Zero LL in at least half the dev
seasons) for the both-pass rule. Both-pass rule: if Gate Zero and
a variant both pass all legs, the lower pooled virgin 1X2 LL
ships; if only one passes, it ships; if none passes, G-ME verdict
is FAIL and nothing ships.

Mechanical reading: an arm *passes* iff it survives the dev gate
AND passes virgin legs (i)–(ii) (a PROVISIONAL PASS counts as a
pass, recorded as such) AND, for variant arms only, leg (iii).
Gate Zero is exempt from (iii) (it is the comparator). If several
variant arms pass together with Gate Zero, the both-pass rule's
"lower pooled virgin 1X2 LL ships" applies across all passing
arms; ties go to the simpler arm (Gate Zero before SHRINK). If
Gate Zero fails its own dev gate, variants are moot, verdict FAIL,
virgin NOT read.

## Outputs

- Engine: `league/ME-1CFL/engine/goals/` (this league's own
  code: fit/predict/harness modules + a CLI runner).
- Dev results: `league/ME-1CFL/engine/goals/results_dev.json`
  (+ `results_dev.csv`, force-added).
- Fitted parameters for the virgin fit:
  `league/ME-1CFL/engine/goals/fitted_params_virgin.json`.
- Virgin predictions: `league/ME-1CFL/predictions/
  g_me_virgin_predictions.csv` — the shipped arm's predictions,
  one row per 2025/2026 match, with FT lambdas, FT 1X2 / OU (1.5,
  2.5, 3.5) / BTTS probabilities, and 1H/2H lines derived by
  splitting the same lambdas with the frozen ME goals constant
  0.426643 (1H λ = 0.426643·FT λ, 2H λ = 0.573357·FT λ; 1H OU lines
  0.5/1.5/2.5, 2H OU lines 1.5/2.5/3.5, same rho and score-matrix
  machinery). Halves are presentation only, never fitted.
- Verdict: `league/ME-1CFL/reports/G_ME_VERDICT.md`.

Production code and data are untouched. No push. No merge.
