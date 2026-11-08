# Pre-registration — G-FI (FI-Ykkonen goals model)

Frozen: 2026-11-10, before any fitting. Design authority:
`analysis/MODEL_DESIGN.md` (G-FI); features X1 (goals-only fallback —
no xG exists in this feed: no `expected_goals*` key in any of 1,730
payloads, no shotmap), X2 entrant offset ADOPTED, X5; evidence
F1/F2/F3/F4/F6/F7/F8/F9.

**Split decision (Jarvis, board comment 6761468990, 2026-11-10
07:17:39Z): OPSI A — dev ≤ 2024 apa adanya, lanjut ke pra-registrasi
pada split BRIEF.** Jarvis's reasons, recorded verbatim in substance:
(1) the brief already knew the restructure ("restructured after
2023… check the phase structure in step 1") and still suggested
dev ≤ 2024, so (A) is the brief's split, not a move after results;
(2) EDA shows the identity change is NOT a level break — regular-phase
goals/match Kakkonen 2023 3.329 vs Ykkönen 2024 3.326, halves constant
0.4445 vs 0.4594 (inside noise), traits carry across the restructure
at the same weak level as within-Kakkonen pairs; the +0.15 headline
shift is a split-phase composition effect (30 high-scoring split
matches), recorded in F7; (3) (B) dev = 2024 only (n=162) breaks the
multi-season dev gate (leg iii, X2) and would be a split chosen after
seeing EDA — exactly what the frozen-gate rule forbids. The group-level
heterogeneity (A 3.470 / B 3.639 / C 3.034) is a within-dev issue the
pooled dev gate is built to judge: if the pooled model does not
generalise to the single-table virgin, it FAILS there, as designed.
Jarvis's instruction: record the Kakkonen/Ykkönen structure + the
composition effect in the prereg, freeze dev ≤ 2024 / virgin 2025 /
2026 reserve, and go. This prereg does exactly that.

## Kakkonen / Ykkönen structure (frozen, EDA F7/F8/F9)

FotMob league_id 8969 changes identity mid-corpus
(`general.leagueName` in the raw JSON):

- 2021–2023 = **Kakkonen** (old tier 3, THREE parallel groups Lohko
  A/B/C, 36–37 teams/season; 396/438/410 matches incl. promotion
  groups + playoffs 2022–2023) — NOT Ykkönen.
- 2024–2026 = **Ykkönen** (tier 3 after restructuring, 12 teams,
  132 regular + 15 championship + 15 relegation = 162/season).
- Factual tier is the same (tier 3) in both eras. Team continuity is
  high: 11/12 Ykkönen 2024 teams played Kakkonen 2021–2023 (10/12 in
  Kakkonen 2023); 9/12 Ykkönen 2025 teams were in 2024.
- **Level is NOT broken by the identity change.** Regular-phase
  goals/match: Kakkonen 2023 3.329 vs Ykkönen 2024 3.326. Halves
  constant by era: Kakkonen 0.4445 vs Ykkönen 2024 0.4594. Trait
  reliability by era: GF 0.610/0.564, GA 0.660/0.680. Season-to-season
  trait carry across the break (2023→2024, 10 teams): GF 0.33 /
  GA 0.30 — the same weak level as within-Kakkonen pairs
  (2021→2022 GF 0.08 / GA 0.18; 2022→2023 GF 0.35 / GA 0.43).
- **Composition effect (F7).** The 2024 headline level (3.512
  goals/match) is +0.15 above the regular phase (3.326) because of
  the 30 championship/relegation split matches scoring 4.333
  goals/match. The 2025 virgin has the same 30-match split-phase
  mix (15 + 15). Split-phase rows are ordinary rows, kept, never
  filtered — a model fitted on dev-era scoring may over-predict
  virgin totals if the split-phase mix differs; the calibration leg
  (ii) will judge that as frozen.
- **Within-dev heterogeneity (F8).** Kakkonen group levels
  2022–2023: A 3.470 / B 3.639 / C 3.034 goals/match. The pooled DC
  rating anchors the three groups together on only **22 cross-group
  matches in the whole dev era (all 2023)** plus the 2024 single
  table. No group adjustment is made — the pooled dev gate is built
  to fail a model whose pooled ratings do not generalise, and the
  virgin (a single table where every team meets) exposes it. The
  calibration leg (ii) will judge that as frozen.

Reference pattern: programme Dixon-Coles (FI G analogue, IL G port).
Documented port: the FI reference `dc.py` / `arms.py` are carried
over verbatim (iterative sweep optimiser, 14 sweeps, damping 0.7,
+0.25 smoothing, home init 0.28, MAXG = 10, production tau, rho grid
(0.0, −0.05, −0.10, −0.15) by goals log-likelihood, decay HL = 270
days); the harness is adapted from the FI `harness.py` with the naive
trailing-10 baseline added per the IL precedent. The ONLY reference
divergence: the observation is goals-only in every match (the X1
blend's documented fallback), because the Ykkönen/Kakkonen feed
carries no xG in any season.

Phases: all rows are ordinary rows (kakkonen_a/b/c, promotion groups,
playoffs, ykkonen, championship, relegation phase flags carried,
never filtered) per the frozen phase rule in
`analysis/DATA_UNDERSTANDING.md`.

## Arms
1. **Gate Zero** — the unmodified reference above. A team with no
   fitted rating (absent from the training seasons) is predicted at
   league mean (attack/defence exponents 0.0).
2. **SHRINK** — Gate Zero plus: at prediction time a team with n < 6
   prior in-league matches has attack/defence exponents scaled by
   n/6 (counts from the training data only, FI `arms.py` mechanics).
   Expected to be numerically near-inert under season-blocked
   prediction in this league (any team present in a prior season has
   ≥22 prior matches, so n<6 never binds for a team with a fitted
   rating; teams with no fitted rating sit at league mean with
   exponents 0.0, which scaling leaves at 0.0) — same observation as
   CH/NO. It is run and reported anyway; the gate decides.
3. **X2** — SHRINK plus the frozen entrant offset: at prediction
   time, a team in its entrant season has its expected-goals
   multipliers shifted by **g_log = −0.182** (own scoring) and
   **c_log = +0.223** (opponent scoring, i.e. its defence is worse),
   applied as λ multipliers exp(g_log) / exp(c_log) on the SHRINK
   lambdas (FI `arms.py` mechanics). Frozen from EDA F4: 22 dev
   entrant transitions, mean GF diff −0.182 / GA diff +0.235 goals
   per match against the dev scored mean team goals 1.7005/match;
   g_log is the mean GF diff as-is (inside the [log 0.8, log 1.25]
   clamp band), c_log is the mean GA diff **clamped at log 1.25 =
   0.2231** (raw +0.235 exceeds the band). Entrant = a team that
   played no match in the immediately preceding season (EDA F4
   definition); the 22 transitions are listed in
   `analysis/eda_summary.json` (`entrant_transitions_dev`), driven
   by the Kakkonen era (20/22 in 2022–2023; only 2 in 2024). The
   offset applies to the team's fitted rating if it has one from an
   earlier season (returning team), otherwise to the league-mean
   fallback (0.0). Signs are consistent (GF negative in the pooled
   mean, GA positive) and match the FI-Veikkausliiga precedent
   direction (−0.358 / +0.263); opposite to NO, where X2 was
   dropped. X2 is the arm that actually differs in this league,
   because Kakkonen churn puts ~10 fresh entrants per season into
   the scored window. Only 22 transitions underlie the offset, so it
   is noisier than the EC analogue — recorded here, not adjusted for.

## Baselines (both, frozen)
- **Climatology / league base rate**: pooled outcome rates (H/D/A)
  and OU2.5 over-rate over the training seasons only (prior seasons
  pooled), as constant probabilities for every scored match.
- **Naive trailing-10**: for each match, independent Poissons with
  means equal to each team's mean goals scored in its last 10 league
  matches strictly before the match (fewer if fewer exist; if none,
  the training league mean team goals/match). 1X2 and OU2.5
  probabilities from the resulting 11×11 score matrix (MAXG = 10).
  No home advantage, no ratings, no fitted parameter beyond the
  training league mean fallback.

## Dev protocol
Warm-up 2021; evaluation seasons 2022–2024 (pooled n = 1,010),
season-blocked (expanding fit strictly before each season's first
match). Metrics: 1X2 LL, RPS, OU2.5 LL per season and pooled, for
all three arms and both baselines. The dev harness must not read
2025 or 2026 rows.

## Virgin protocol
Virgin = 2025 (n = 162, complete season), read ONCE, only for
dev-passing arms. Fit expands to all matches ≤ 2024. Calibration:
mean predicted − actual for home-win rate and OU2.5 over-rate,
SE = sd(p_i − y_i)/√n. 2026 (in progress, n = 162) is untouched as
confirmatory reserve.

## GATE LEGS (verbatim, frozen)
Dev gate — pooled dev 1X2 LL, RPS and OU2.5 LL of an arm must beat
BOTH baselines (climatology and naive trailing-10), else the arm is
dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's
AND ≤ each baseline's, and its virgin OU2.5 LL ≤ each baseline's;
(ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for
home-win rate and for OU2.5 over-rate, SEs reported; a breach within
1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL;
(iii) per-season sign check on dev (variant 1X2 LL ≤ Gate Zero 1X2
LL in at least half the dev seasons, i.e. ≥ 2 of 3) for the
both-pass rule. Both-pass rule: if Gate Zero and a variant both pass
all legs, the lower pooled virgin 1X2 LL ships; if only one passes,
it ships; if none passes, G-FI verdict is FAIL and nothing ships.
Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts) AND, for variants,
leg (iii); Gate Zero is exempt from (iii). Ties → simpler arm (Gate
Zero before SHRINK before X2). If Gate Zero fails its dev gate,
variants are moot, verdict FAIL, virgin NOT read.

## Evaluation lines (frozen, EDA F6)
Primary: 1X2 and OU 2.5 (dev scored over-rates 1.5: 0.846, 2.5:
0.650, 3.5: 0.436; n = 1,010). The closest-to-0.5 line pick on dev
is OU 3.5 (0.436), recorded as a diagnostic — the gate lines stay
1X2 + OU 2.5 per the programme. Home win rate 0.471, draw rate
0.198 in the same window. Dev scored mean team goals 1.7005/match
(3,435 goals / 1,010 matches / 2). Halves presentation via the
frozen goals constant 0.4463 only (config.yaml); no halves constant
exists for any count market. Predictions-only: no FI
odds/settlement source in-system.

## Known risks (recorded, not adjusted)
- **Cross-group identification (EDA F8).** See structure section
  above: 22 cross-group matches anchor three Kakkonen groups; group
  C runs ~0.35–0.60 goals/match below group B. If the weak anchoring
  mis-rates cross-group strength, the dev gate (which pools all
  three groups) may still pass while the virgin — a single table
  where every team meets — exposes it. The calibration leg (ii)
  will judge that as frozen.
- **2024 split-phase scoring (EDA F7).** The 30 championship /
  relegation matches in dev score 4.333 goals/match vs 3.326 in the
  regular phase. They are ordinary rows, kept, never filtered; a
  model fitted on dev-era scoring may over-predict virgin totals if
  the split-phase mix differs. The calibration leg (ii) will judge
  that as frozen.
- **Virgin size.** Virgin 2025 is n=162 — small, so the gate's
  sampling-noise band is wide; apply the gate as written, do not
  soften it (per the brief).

## Outputs
Engine `engine/goals/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/g_fi_virgin_predictions.csv` (1H/2H presentation via
frozen goals constant 0.4463). Verdict `reports/G_FI_VERDICT.md`.
