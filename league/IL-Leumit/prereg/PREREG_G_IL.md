# Pre-registration — G-IL (Israel Leumit League goals model)

Frozen: 2026-11-09, before any fitting. Branch `build/il-leumit`.
Design authority: `league/IL-Leumit/analysis/MODEL_DESIGN.md`
(candidate G-IL); features per `league/IL-Leumit/analysis/FEATURES.md`
(X1 goals-only, X2 mover offset, SHRINK §2); evidence per
`league/IL-Leumit/analysis/EDA.md` (F1/F2/F4). Reference
implementation: production Dixon-Coles in `model_v2.py` (class `DC`,
`probs`), production hl = 270; J1 analogue `league/J1/prereg/PREREG_G_J1.md`.

## Reference architecture (all arms share this unless an arm says otherwise)

- Dixon-Coles fit, copied pattern from production `model_v2.py`:
  iterative multiplicative updates, 14 sweeps, damping 0.7, +0.25
  smoothing, home advantage `h` fitted (init 0.28), attack `a` and
  defence `d` per team (init 0), score matrix to MAXG = 10 with the
  production `tau` low-score correction.
- Rho: chosen per fit from the grid (0.0, −0.05, −0.10, −0.15) by
  weighted log-likelihood on goals only, exactly as production.
- Observation (X1): goals only. No xG exists anywhere in this corpus
  (stats coverage 0%), so the production blend's goals-only fallback
  is the observation for every match — definitional, no search.
- Time decay: weight w = 0.5 ** ((cutoff − match_date).days / 270).
  Half-life 270 days is the production value, frozen — no search.
- Fit scope for a target season S: all IL-Leumit matches with date
  strictly before the first match date of S (expanding window,
  season-blocked: one fit per target season, whole season predicted
  from that fit). Both phases (regular + split) are in the fit.
- Teams are keyed by FotMob team ID. Teams unseen in training start
  at the league mean (a = d = 0).

## Arms

1. **Gate Zero** — the unmodified reference above. Movers start at
   the league mean.
2. **Arm SHRINK** (sanctioned G-J2-lesson arm; FEATURES §2) — Gate
   Zero plus exactly one change at prediction time: for a team with
   fewer than 6 prior in-league matches in the training window, its
   fitted attack and defence ratings are shrunk toward the league
   mean: `a *= n/6`, `d *= n/6` where n = its prior in-league match
   count (n = 0 ⇒ a = d = 0, identical to Gate Zero's unseen rule;
   the arm bites exactly for teams with 1–5 prior matches). Nothing
   else changes.
3. **Arm X2** — Gate Zero plus mover tier priors (feature X2, EDA
   F4). A club is a *mover* for target season S when it did not play
   in Leumit in the season immediately preceding S (membership by
   team ID), classified by the immediately preceding season:
   *down-mover* if it played that season in Ligat ha'Al (league_id
   127, team ID present in that league's warehouse matches for that
   season), otherwise *up-mover* (tier 3 is not in the warehouse).
   For a mover, at prediction time in season S only, with mu = the
   decay-weighted mean goals per team per match in the training
   window:
   - down-mover: attack `a += log((mu + 0.291) / mu)`; defence
     `d += log(max(mu − 0.239, 0.10) / mu)`
   - up-mover: attack `a += log(max(mu − 0.080, 0.10) / mu)`;
     defence `d += log((mu + 0.109) / mu)`
   where +0.291 / −0.239 / −0.080 / +0.109 are the frozen F4
   magnitudes (entry-season GF/GA deltas vs league mu, pooled over
   the corpus's entry seasons 2022/2023–2025/2026, n = 8
   team-seasons per kind). The offset is added to the fitted rating
   (league mean 0 for a first-time club). Clubs with no
   immediately-preceding-season record anywhere start at the league
   mean in every arm. Nothing else changes.

## Dev protocol

- Dev period: seasons 2021/2022–2024/2025. Season 2021/2022 is the
  initial training window; evaluation seasons are 2022/2023,
  2023/2024, 2024/2025 under the expanding season-blocked
  walk-forward above. Pooled dev n = 888.
- Metrics per arm per season and pooled: mean 1X2 log-loss (natural
  log), mean RPS (outcomes ordered H, D, A), mean OU2.5 log-loss
  (binary, on P(over 2.5)).
- Baselines: climatology — for target season S, the pooled outcome
  rates (home win / draw / away win) and OU2.5 over-rate of all
  IL-Leumit seasons strictly before S.
- The dev harness must not read season "2025/2026" or "2026/2027"
  rows at all. Virgin data is touched only by the separate virgin
  step, once, after dev results are frozen in the results file.

## Virgin protocol

- Virgin window: season "2025/2026" (n = 296, complete). Fit = all
  IL-Leumit matches dated before the first 2025/2026 match
  (seasons 2021/2022–2024/2025). Read ONCE, after dev freezes, and
  only for arms that pass the dev gate.
- Virgin climatology: pooled 2021/2022–2024/2025 outcome rates and
  OU2.5 over-rate.
- Calibration per arm: (i) mean predicted home-win probability minus
  actual home-win rate; (ii) mean predicted P(over 2.5) minus actual
  over-rate. SE = sd(pred_i − y_i) / √n over the 296 matches.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-IL verdict is FAIL and nothing ships.

Reading of the legs, fixed here so the verdict is mechanical:

- An arm *passes* iff it survives the dev gate AND passes virgin
  legs (i)–(ii) (a PROVISIONAL PASS counts as a pass, recorded as
  such) AND, for variant arms only, leg (iii). Gate Zero is exempt
  from (iii) (it is the comparator).
- If several variant arms pass together with Gate Zero, the
  both-pass rule's "lower pooled virgin 1X2 LL ships" applies across
  all passing arms; ties go to the simpler arm (Gate Zero before
  SHRINK before X2).
- If Gate Zero fails its own dev gate, variant arms are moot: the
  verdict is FAIL and the virgin is NOT read.

## Outputs

- Engine: `league/IL-Leumit/engine/goals/` (this league's own code:
  fit/predict/harness modules + a CLI runner + README).
- Dev results: `league/IL-Leumit/engine/goals/results_dev.json` (+ CSV).
- Virgin results: `league/IL-Leumit/engine/goals/results_virgin.json`.
- Fitted parameters for the virgin fit:
  `league/IL-Leumit/engine/goals/fitted_params_virgin.json`.
- Virgin predictions (PASS only):
  `league/IL-Leumit/predictions/g_il_virgin_predictions.csv` — the
  shipped arm's predictions, one row per 2025/2026 match, with FT
  lambdas and FT 1X2 / OU (1.5, 2.5, 3.5) / BTTS probabilities.
  FT presentation only: no halves constants exist for this league
  (no period splits), so no 1H/2H lines are produced.
- Verdict: `league/IL-Leumit/reports/G_IL_VERDICT.md`.

Production code and data are untouched. No push. No merge.
