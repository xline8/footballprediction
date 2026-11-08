# Pre-registration — G-CY2 (Cyprus 2. Division goals)

Frozen: 2026-11-10, before any fitting. Design authority:
`analysis/MODEL_DESIGN.md`; data decisions: `analysis/FEATURES.md`;
evidence: `analysis/EDA.md` (F1/F2/F3/F4/F5). Target: goals,
primary OU2.5, with home-win calibration legs. Dev scored n = 682
(2022/2023–2024/2025); training seed 2021/2022; virgin 2025/2026
(n = 232); confirmatory 2026/2027. All phases are ordinary matches,
phase flagged, no phase feature. Calibration = actual − predicted.
The dev primary over-rate is 0.491 at OU2.5 (dev-scored window
2022/2023–2024/2025, n = 682).

## Reference architecture (all arms share this unless an arm says otherwise)

- Dixon-Coles fit, copied pattern from production `model_v2.py`
  via the sibling G-CY implementation (`league/CY-1Division/engine/
  goals/dc.py`): iterative multiplicative updates, 14 sweeps,
  damping 0.7, +0.25 smoothing, home advantage `h` fitted (init
  0.28), attack `a` and defence `d` per team (init 0), score matrix
  to MAXG = 10 with the production `tau` low-score correction.
- Rho: chosen per fit from the grid (0.0, −0.05, −0.10, −0.15) by
  weighted log-likelihood on goals only, exactly as production.
- Observation: goals only (no xG exists in this league — the
  reference blend's documented fallback).
- Time decay: weight w = 0.5 ** ((cutoff − match_date).days / 270).
  Half-life 270 days is the production value, frozen — no search.
- Fit scope for a target season S: all CY-2Division matches with
  date strictly before the first match date of S (expanding window,
  season-blocked: one fit per target season, whole season predicted
  from that fit).
- Teams unseen in training start at the league mean (a = d = 0).

## Arms

1. **Gate Zero** — the unmodified reference above. Movers start at
   the league mean.
2. **Arm X2** — Gate Zero plus the cross-tier prior (feature X2,
   EDA F4). A club is a *relegated-in mover* for target season S
   when its most recent prior season is the season immediately
   preceding S, it played that season in CY-1Division (team id
   present in `data/cy1_team_seasons.json` for that season), and it
   did not play CY-2Division in that season. For a relegated-in
   mover, at prediction time in season S only:
   - attack: `a += log((mu + 0.08) / mu)`
   - defence: `d += log(max(mu − 0.21, 0.10) / mu)`
   where mu is the decay-weighted mean goals per team per match in
   the training window, and +0.08 / −0.21 are the F4 magnitudes
   (GF +0.08, GA −0.21 per match on CY-1→CY-2 arrival, n = 8
   team-seasons, pre-virgin transitions only). The offset is added
   to the fitted rating (league mean 0 for a first-time club).
   Clubs with no immediately-preceding-season record in CY-1 or
   CY-2 start at the league mean in every arm. (No promoted-mover
   case exists into CY-2 from a higher tier other than CY-1, and
   no offset is claimed for brand-new ids — EDA F4 finds them
   league-average on arrival.)
3. **Arm SHRINK** — Gate Zero plus the G-J2 post-mortem shrinkage:
   a team's attack/defence ratings are multiplied by
   `min(1.0, counts / 6.0)` where counts = its matches in the
   training window. Expected to coincide with Gate Zero in this
   league (every non-new team has ~30 training matches; new teams
   are already at the mean); run anyway and gated like any arm.

## Dev protocol

- Dev period: seed 2021/2022; evaluation seasons 2022/2023,
  2023/2024, 2024/2025 under the expanding season-blocked
  walk-forward above. Pooled dev = the three evaluation seasons
  combined (n = 682).
- Metrics per arm per season and pooled: mean 1X2 log-loss
  (natural log), mean RPS (outcomes ordered H, D, A;
  RPS = 0.5 · Σ_k (Σ_{j≤k} p_j − Σ_{j≤k} y_j)²), mean OU2.5
  log-loss (binary, on P(over 2.5)).
- Baselines: climatology — for target season S, the pooled outcome
  rates (home win / draw / away win) and OU2.5 over-rate of all
  CY-2Division seasons strictly before S. The same climatology
  probabilities score LL, RPS and OU LL for that season.
- The dev harness must not read season "2025/2026" or "2026/2027"
  rows at all. Virgin data is touched only by the separate virgin
  step, once, after dev results are frozen in the results file.

## Virgin protocol

- Virgin window: season "2025/2026" (n = 232, complete). Fit = all
  CY-2Division matches dated before the first 2025/2026 match
  (seasons 2021/2022–2024/2025). Read ONCE, after dev freezes.
- Virgin climatology: pooled 2021/2022–2024/2025 outcome rates and
  OU2.5 over-rate.
- Calibration per arm: (i) mean predicted home-win probability
  minus actual home-win rate; (ii) mean predicted P(over 2.5)
  minus actual over-rate. Standard error of each difference:
  SE = sd(pred_i − y_i) / √n over the 232 matches, reported with
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
ships; if only one passes, it ships; if none passes, G-CY2 verdict
is FAIL and nothing ships.

Mechanical reading: an arm *passes* iff it survives the dev gate
AND passes virgin legs (i)–(ii) (a PROVISIONAL PASS counts as a
pass, recorded as such) AND, for variant arms only, leg (iii).
Gate Zero is exempt from (iii) (it is the comparator). If several
variant arms pass together with Gate Zero, the both-pass rule's
"lower pooled virgin 1X2 LL ships" applies across all passing
arms; ties go to the simpler arm (Gate Zero before X2 before
SHRINK). If Gate Zero fails its own dev gate, variants are moot,
verdict FAIL, virgin NOT read.

## Outputs

- Engine: `league/CY-2Division/engine/goals/` (this league's own
  code: fit/predict/harness modules + a CLI runner).
- Dev results: `league/CY-2Division/engine/goals/results_dev.json`
  (+ `results_dev.csv`, force-added).
- Fitted parameters for the virgin fit:
  `league/CY-2Division/engine/goals/fitted_params_virgin.json`.
- Virgin predictions: `league/CY-2Division/predictions/
  g_cy2_virgin_predictions.csv` — the shipped arm's predictions,
  one row per 2025/2026 match, with FT lambdas, FT 1X2 / OU (1.5,
  2.5, 3.5) / BTTS probabilities, and 1H/2H lines derived by
  splitting the same lambdas with the frozen CY-2 goals constant
  0.4351 (1H λ = 0.4351·FT λ, 2H λ = 0.5649·FT λ; 1H OU lines
  0.5/1.5/2.5, 2H OU lines 1.5/2.5/3.5, same rho and score-matrix
  machinery). Halves are presentation only, never fitted.
- Verdict: `league/CY-2Division/reports/G_CY2_VERDICT.md`.

Production code and data are untouched. No push. No merge.
