# Pre-registration — G-ESPF (ES-PrimeraFederacion goals model)

Frozen: 2026-11-10, before any fitting. Branch
`build/es-primera-federacion`.
Design authority: `league/ES-PrimeraFederacion/analysis/MODEL_DESIGN.md`
(G-ESPF); features per `analysis/FEATURES.md` (X2 mover tier offset;
X1 never-born — no xG anywhere in the corpus); evidence per
`analysis/EDA.md` (F1/F3/F4). Reference: production Dixon-Coles in
`model_v2.py` (class `DC`), hl = 270; analogues:
`league/ES-LaLiga2/prereg/PREREG_G_ES.md` (goals-only construction,
SHRINK/X2 formulation) and `league/ENG-Championship/prereg/
PREREG_G_ENGCH.md` (X2 formulation). Correction note: the sibling
league used for X2 mover lookups is LaLiga2, FotMob **140** — not
87 (87 is LaLiga, the production top-5 tier-1 league, untouched
here); Primera Federación itself is FotMob 8968.

## Reference architecture (all arms share unless an arm says otherwise)

- Dixon-Coles fit, copied pattern from production `model_v2.py`:
  iterative multiplicative updates, 14 sweeps, damping 0.7, +0.25
  smoothing, home advantage fitted (init 0.28), attack/defence per
  team (init 0), score matrix MAXG = 10, production `tau` correction.
- Rho per fit from grid (0.0, −0.05, −0.10, −0.15) by weighted
  log-likelihood on goals only, as production.
- Observation = **goals only**. The production blend's xG half does
  not exist in this league at all (`expected_goals` in 0 of 4,081
  matches; no stats/shotmap era in any season) — goals-only is the
  reference implementation's own documented fallback (G-J2
  precedent), frozen here by design: no xG arm is built on zero
  eras.
- Time decay w = 0.5 ** ((cutoff − match_date).days / 270) — frozen,
  no search.
- Fit scope for target season S: all PF matches dated strictly
  before the first match date of S (expanding, season-blocked).
  Play-off matches are ordinary rows (PREPROCESSING rule 3); awarded
  and extra-time scores are used as-is (DATA_UNDERSTANDING §3).
- Teams unseen in training start at the league mean (a = d = 0).
  Team identity is FotMob team_id everywhere (PREPROCESSING rule 9).
- Two-group note (MODEL_DESIGN §1, frozen, no arm): Gate Zero fits
  one rating set over all 40 teams. Within-group predictions are
  invariant to the per-group shift; the cross-group offset is pinned
  only by the play-off matches (7–14/season, cross-group by design)
  plus the shared home advantage. A group-split fit was considered
  and rejected before fitting.

## Arms

1. **Gate Zero** — the unmodified reference above.
2. **Arm SHRINK** (sanctioned G-J2-lesson arm; FEATURES F4 context)
   — Gate Zero plus exactly one change at prediction time: for a
   team with fewer than 6 prior in-league matches in the training
   window, its fitted attack and defence ratings are shrunk toward
   the league mean: `a *= n/6`, `d *= n/6` where n = its prior
   in-league match count (n = 0 ⇒ a = d = 0, identical to Gate
   Zero's unseen rule; the arm bites exactly for teams with 1–5
   prior matches — the season-opener failure mode). **Pre-recorded
   expectation: this arm is degenerate under season-blocked fitting
   in this league.** Prior in-league counts at a season start are 0
   (new club, 14/season) or ≥38 (returning club), so n/6 only ever
   takes the values 0 or 1 and the arm should come out bit-identical
   to Gate Zero (the G-ES verdict recorded the same construction).
   It runs as an implementation check; if it is NOT bit-identical,
   that is a bug, not a finding. Nothing else changes.
3. **Arm X2** — Gate Zero plus mover tier priors (feature X2, EDA
   F4), in the ENGCH X2 formulation. A club is a *mover* for target
   season S when it did not play in Primera Federación in season
   S−1 and it enters in S. Membership is keyed on **FotMob team_id**,
   computed from warehouse payloads: prior-season LaLiga2 team ids
   are read from the LaLiga2 payloads (league 140, season S−1);
   prior-season PF ids from the PF payloads. A mover is
   `from LaLiga2` iff its id is in the prior-season LaLiga2 set
   (and not in the prior-season PF set); otherwise it is `from
   below` (Segunda Federación, not in the warehouse). The id-keyed
   mover lists must equal the EDA name-keyed lists (exactly 4 + 10
   per season) — a failed equality is a bug, checked before any
   virgin read. For a mover, at prediction time in season S only,
   with mu = the decay-weighted mean goals per team per match in
   the training window:
   - from LaLiga2: attack `a += log((mu + 0.081) / mu)`; defence
     `d += log((mu - 0.150) / mu)`
   - from below: attack `a += log(max(mu - 0.054, 0.10) / mu)`;
     defence `d += log((mu + 0.011) / mu)`
   where +0.081 / −0.150 / −0.054 / +0.011 are the frozen F4
   magnitudes (entry-season GF/GA deltas vs league mu 1.1581, dev
   entry seasons 2022/2023–2024/2025 only — no frozen input touches
   the virgin). The offset is added to the fitted rating (league
   mean 0 for a first-time club). Nothing else changes.

## Dev protocol

- Training seed = 2021/2022; evaluation seasons 2022/2023, 2023/2024,
  2024/2025 (pooled n = 2,322) under the season-blocked walk-forward.
- Metrics per arm per season and pooled: mean 1X2 LL, mean RPS
  (H, D, A), mean OU2.5 LL. Baselines: climatology — for target
  season S, pooled outcome rates + OU2.5 over-rate of all seasons
  strictly before S.
- The dev harness must not read 2025/2026 or 2026/2027 rows at all.

## Virgin protocol

- Virgin = 2025/2026 (n = 772, complete), read ONCE, only for arms
  passing the dev gate, after dev results are frozen. Fit = all
  matches before the first 2025/2026 match date. Climatology =
  pooled 2021/2022–2024/2025 rates. Calibration: mean predicted −
  actual for home-win rate and OU2.5 over-rate, SE = sd(p_i − y_i)/√n.
- 2026/2027 (partial, n = 220) is reserved as the confirmatory
  window and is NOT read in this build.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-ESPF verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such)
AND, for variant arms, leg (iii); Gate Zero is exempt from (iii).
Ties go to the simpler arm (Gate Zero before SHRINK before X2). If
Gate Zero fails its own dev gate, variants are moot, verdict FAIL,
virgin NOT read.

## Outputs

Engine `league/ES-PrimeraFederacion/engine/goals/`; dev results
`results_dev.json` (+ CSV); virgin `results_virgin.json`; fitted
params `fitted_params_virgin.json`; on PASS, virgin predictions
`league/ES-PrimeraFederacion/predictions/g_espf_virgin_predictions.csv`
(shipped arm; 1H/2H presentation via frozen goals constant 0.4301).
Verdict: `league/ES-PrimeraFederacion/reports/G_ESPF_VERDICT.md`.
Non-buildable candidates (S/C/K/T) are recorded in the verdict
file's feasibility section with their payload-level evidence; no
prereg, engine, or virgin read exists for them. Production code
untouched. No push. No merge.
