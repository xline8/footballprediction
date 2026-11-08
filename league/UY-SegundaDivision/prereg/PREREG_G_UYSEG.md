# Pre-registration — G-UYSEG (UY-SegundaDivision goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/uy-segunda-division`.
Design authority: `league/UY-SegundaDivision/analysis/MODEL_DESIGN.md` (G-UYSEG);
features per `analysis/FEATURES.md` (X1 goals-only form, X2, fitted home
advantage); evidence per `analysis/EDA.md` (F1/F2/F3/F4/F11) and
`analysis/eda_summary.json`.
Reference: production Dixon-Coles in `model_v2.py` (class `DC`),
hl = 270; analogues: `PREREG_G_SK2.md`, `PREREG_G_UY.md` (sibling
UY-LigaAUF, same scores-only data pattern).

## Reference architecture (all arms share unless an arm says otherwise)

- Dixon-Coles fit, copied pattern from production `model_v2.py`:
  iterative multiplicative updates, 14 sweeps, damping 0.7, +0.25
  smoothing, home advantage fitted (init 0.28), attack/defence per
  team (init 0), score matrix MAXG = 10, production `tau` correction.
- Rho per fit from grid (0.0, −0.05, −0.10, −0.15) by weighted
  log-likelihood on goals only, as production.
- Observation: **goals only** (X1 fallback form — xG is absent in
  every payload of this league; there is no blend).
- Time decay w = 0.5 ** ((cutoff − match_date).days / 270) — frozen.
- Fit scope for target season S: all finished UY-SegundaDivision matches
  dated strictly before the first match date of S (expanding,
  season-blocked).
- Teams unseen in training start at the league mean (a = d = 0).

## Arms

1. **Gate Zero** — the unmodified reference above.
2. **Arm SHRINK** (sanctioned G-J2-lesson arm; FEATURES/EDA F4
   context) — Gate Zero plus exactly one change at prediction time:
   for a team with fewer than 6 prior in-league matches in the
   training window, its fitted attack and defence ratings are
   shrunk toward the league mean: `a *= n/6`, `d *= n/6` where n =
   its prior in-league match count (n = 0 ⇒ a = d = 0, identical to
   Gate Zero's unseen rule). Nothing else changes. Expected to bite
   mainly in 2022 (thin 85-match 2021 seed; several clubs with
   partial 2021 records) and on tier-3 entrants with short histories.
   Ties go to Gate Zero.
3. **Arm X2** — Gate Zero plus the relegated-mover offset (feature X2,
   EDA F4). A club is a *relegated mover* for target season S when
   it played the immediately preceding season in UY-LigaAUF
   (FotMob id 161) and plays Segunda in S, keyed by FotMob team id
   (names are unstable in this league — accent variants share one
   id: Fenix/Fénix 7808, Paysandu/Paysandú 4660). At prediction
   time in season S only, the mover's own scoring lambda is
   multiplied by `max(mu + dGF, 0.10) / mu` and the opponent's
   scoring lambda against it by `(mu + dGA) / mu`, where mu is the
   fit's decay-weighted mean goals per team per match in the
   training window and (dGF, dGA) are the cumulative mean
   first-season deviations of relegated-mover transitions
   **completed before S** (EDA F4, frozen values below). Clubs
   entering from tier 3 (no warehouse league) have no prior-season
   record and start at the league mean in every arm. Movers by
   season (team id — canonical name):
   - 2022: {1835 Villa Espanola, 1838 Progreso, 188312 Sud America}
   - 2023: {924934 Albion, 2220 Cerrito, 2221 Rentistas}
   - 2024: {395613 Montevideo City Torque, 1319664 La Luz, 4669 Plaza Colonia}
   - 2025: {7808 Fenix, 4421 Rampla Juniors, 1833 Deportivo Maldonado}
   - 2026 (virgin): {4424 Miramar Misiones, 6381 River Plate, 4669 Plaza Colonia}
   Frozen (dGF, dGA) by target season — cumulative over completed
   transitions only:
   - S = 2022 → (0.0, 0.0), n_prior = 0 (arm ≡ Gate Zero that season)
   - S = 2023 → (−0.129264, +0.179378), n_prior = 3
   - S = 2024 → (−0.044284, +0.134240), n_prior = 6
   - S = 2025 → (+0.004892, +0.066170), n_prior = 9
   - S = 2026 (virgin) → (−0.017161, +0.040064), n_prior = 12
   Recorded honestly: the 12-transition dev signal is ~null (mean GF
   −0.017, 7 negative / 5 positive; mean GA +0.040, 5 negative / 7
   positive) — the opposite of the expected relegated-team boost and
   far weaker than the sibling LigaAUF promoted-entrant signal. X2
   is registered as a gated arm anyway (the mechanism is measurable
   and the offsets are frozen before fitting); the dev gate decides
   whether it ships. The EDA log-offset equivalents (mu = 1.1095)
   are reported in `eda_summary.json` for reference only; the engine
   applies the (dGF, dGA) diffs with the fit's own mu, exactly as
   the SK-2Liga engine does.

## Dev protocol

- Training seed = 2021 (85 finished matches); evaluation seasons
  2022, 2023, 2024, 2025 (pooled n = 863) under the season-blocked
  walk-forward.
- Metrics per arm per season and pooled: mean 1X2 LL, mean RPS
  (H, D, A), mean OU2.5 LL. Primary line OU2.5 (dev pooled
  over-rate 0.373, closest to 50% among 1.5/2.5/3.5 — EDA F11).
  Baselines: climatology — for target season S, pooled outcome
  rates + OU2.5 over-rate of all seasons strictly before S. Also
  report the naive trailing-10 baseline (team trailing-10 goal
  rates) for the 1X2 LL comparison in the verdict.
- The dev harness must not read 2026 rows at all.

## Virgin protocol

- Virgin = 2026 (n = 218, TRANSITIONAL — last match 2026-11-01, 12
  fewer matches than 2025; completeness not confirmed), read ONCE,
  only for arms passing the dev gate, after dev results are frozen.
  Fit = all finished matches before the first 2026 match date.
  Climatology = pooled 2021–2025 rates. Calibration: mean predicted
  − actual for home-win rate and OU2.5 over-rate, SE = sd(p_i − y_i)/√n.
- If the virgin read shows the season is incomplete (e.g. teams with
  visibly partial schedules beyond the known name-variant merge),
  record that in the verdict; the read still counts as the single
  virgin read and is not repeated.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-UYSEG verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such)
AND, for variant arms, leg (iii); Gate Zero is exempt from (iii).
Ties go to the simpler arm (Gate Zero before SHRINK before X2).
If Gate Zero fails its own dev gate, variants are moot, verdict
FAIL, virgin NOT read.

## Outputs

Engine `league/UY-SegundaDivision/engine/goals/`; dev results
`results_dev.json` (+ CSV, force-added); virgin `results_virgin.json`;
fitted params `fitted_params_virgin.json`; on PASS, virgin predictions
`league/UY-SegundaDivision/predictions/g_uyseg_virgin_predictions.csv`
(shipped arm; 1H/2H presentation via frozen goals constant 0.4329).
Verdict: `league/UY-SegundaDivision/reports/G_UYSEG_VERDICT.md`.
Production code untouched. No push. No merge.
