# Phase 4 — Model Design: ES-PrimeraFederacion Candidates

Rules inherited from `league/J1/analysis/MODEL_DESIGN.md`: every
candidate names its production reference, Gate Zero is the unmodified
reference fitted per league, variants come only from FEATURES.md
adopted arms (max 2–3 per candidate), gates are the program's frozen
legs, a FAIL is a complete outcome. Feature consumption: FEATURES.md.
Worked analogues: ES-LaLiga2 (same country, same churn shape,
play-offs as ordinary rows) and ENG-Championship (2nd tier,
play-offs, heavy churn) — with one structural difference no other
league in the program has: **two groups of 20 that never meet in
the regular season** (§1 below).

Shared frame: dev = walk-forward over 2021/2022–2024/2025 (train
seed 2021/2022; evaluation 2022/2023–2024/2025, pooled n=2,322,
season-blocked); virgin = 2025/2026 (n=772, complete — see
DATA_UNDERSTANDING §1 for the frozen choice), read ONCE and only for
arms passing the dev gate; 2026/2027 (partial, n=220) reserved
un-read as the confirmatory window. Baselines: climatology
(prior-seasons H/D/A rates + OU2.5 over-rate) for goals.
Calibration rule: |breach| ≤ 1pp clean PASS; ≤ 1 SE PROVISIONAL
PASS; else FAIL. Primary line = the .5 line whose dev-eval over-rate
is closest to 0.5 (OU2.5 at 0.4027; OU1.5 0.6641, OU3.5 0.1938).
All model state is keyed on FotMob team_id (Phase 2 rule 9).

| Candidate | Reference | Primary line (dev-eval over-rate) | Arms |
|---|---|---|---|
| G-ESPF goals | production DC (model_v2 pattern), **goals-only** (X1 never-born — documented fallback, J2 precedent) | OU 2.5 (0.403) + 1X2 LL/RPS | Gate Zero; SHRINK (thin-data prior — sanctioned G-J2-lesson arm); X2 mover tier offset (F4 magnitudes, LaLiga2/from-below) |
| S-ESPF SOT | — | — | NOT BUILDABLE (no stats, no shotmap, 0/4,081) |
| C-ESPF corners | — | — | NOT BUILDABLE (no stats, 0/4,081) |
| K-ESPF cards | — | — | NOT BUILDABLE (card events 995 total, ~0.24/match, in 18–25% of matches; no stats feed) |
| T-ESPF total shots | — | — | NOT BUILDABLE (no stats, no shotmap, 0/4,081) |

## 1. The two-group question (frozen here, before fitting)

Gate Zero fits **one** Dixon-Coles rating set over all 40 teams
(the unmodified production pattern). The two groups never play each
other in the regular season, so the likelihood has one weakly
identified direction per group: adding a constant to every attack
rating in a group and subtracting it from every defence rating in
the same group leaves all within-group lambdas unchanged. That
direction is pinned only by the play-off matches (7–14/season, all
cross-group by design) plus the shared home advantage. This is a
limitation to record, not a reason to redesign Gate Zero:

- Within-group predictions — 760/774 matches a season — are
  **invariant** to the per-group shift (they use `a_home + d_away`
  inside one group only). The fit's quality where it matters is
  unaffected by the identification gap.
- Play-off predictions (1.8% of rows) rely on the weak cross-group
  pin. They are included as ordinary rows and scored as ordinary
  rows; if the pooled fit is bad, the dev gate will say so.
- A group-split fit (two DC models + a cross-model play-off rule)
  was considered and **rejected**: it diverges from the unmodified
  Gate Zero reference, and play-off predictions would need
  cross-model calibration with no shared scale. No arm in this
  prereg implements it.

## 2. G-ESPF arms

- **Gate Zero** — production DC pattern, unmodified: iterative
  multiplicative updates, 14 sweeps, damping 0.7, +0.25 smoothing,
  home advantage fitted (init 0.28), attack/defence per team
  (init 0), score matrix MAXG = 10, production `tau` correction,
  rho from grid (0.0, −0.05, −0.10, −0.15) by weighted
  log-likelihood on goals only. Observation = **goals only** (the
  production blend's xG half does not exist in this league at all).
  Time decay w = 0.5 ** ((cutoff − match_date).days / 270), frozen.
  Fit scope for target season S: all PF matches dated strictly
  before the first match date of S (expanding, season-blocked).
  Teams unseen in training start at the league mean (a = d = 0).
- **SHRINK** (sanctioned G-J2-lesson arm) — Gate Zero plus exactly
  one change at prediction time: for a team with fewer than 6 prior
  in-league matches in the training window, its fitted attack and
  defence ratings are shrunk toward the league mean: `a *= n/6`,
  `d *= n/6` where n = its prior in-league match count. **Pre-recorded
  expectation: this arm is degenerate under season-blocked fitting
  in this league.** Prior in-league counts at a season start are 0
  (new club, 14/season) or ≥38 (returning club, 38 regular matches
  minimum), so the n/6 factor only ever takes the values 0 (= Gate
  Zero's unseen rule) or 1 — the arm should come out bit-identical
  to Gate Zero, as the G-ES verdict recorded for the same
  construction. It still runs, as a check on the implementation; if
  it is NOT bit-identical, that is a bug, not a finding.
- **X2** — Gate Zero plus mover tier priors (feature X2, EDA F4),
  in the ENGCH X2 formulation. A club is a *mover* for target
  season S when it did not play in Primera Federación in season
  S−1 and it enters in S. Membership is keyed on **FotMob team_id**,
  computed from warehouse payloads (deviation from the ES name-based
  method, forced by the rename cases in DATA_UNDERSTANDING §1: no
  accent-normalisation bridges `Barcelona B` → `Barca Atletic`):
  prior-season LaLiga2 team ids are read from the LaLiga2 payloads
  (league 140, season S−1); prior-season PF ids from the PF payloads.
  A mover is `from LaLiga2` iff its id is in the prior-season
  LaLiga2 set (and not in the prior-season PF set); otherwise it is
  `from below` (Segunda Federación). For a mover, at prediction time
  in season S only, with mu = the decay-weighted mean goals per team
  per match in the training window:
  - from LaLiga2: attack `a += log((mu + 0.081) / mu)`; defence
    `d += log((mu - 0.150) / mu)`
  - from below: attack `a += log(max(mu - 0.054, 0.10) / mu)`;
    defence `d += log((mu + 0.011) / mu)`
  where +0.081 / −0.150 / −0.054 / +0.011 are the frozen F4
  magnitudes (entry-season GF/GA deltas vs league mu 1.1581, dev
  entry seasons 2022/2023–2024/2025 only). The offset is added to
  the fitted rating (league mean 0 for a first-time club). Nothing
  else changes. Verification: the id-keyed mover lists must equal
  the EDA name-keyed lists (4 + 10 per season) exactly.

## 3. Non-buildable candidates (recorded, not deferred)

S/C/K/T are not buildable on availability — the payload-level
evidence is in DATA_UNDERSTANDING §2 and EDA F5–F9. There is no
rescue arm, no proxy target (the card event feed is a sparse
subset of unknown selection; inventing a cards target from it
would be fabrication, not modelling), and no deferred design. If
FotMob's coverage of this league changes, the feasibility matrix is
re-opened by a new prereg — not by this one.

## Notes

- G-ESPF is goals-only **by design**, per Phase 1: there is no xG
  anywhere in the corpus (0/4,081), not merely an era break. Gate
  Zero here is the reference architecture with its documented
  goals-only observation (exactly G-J2's construction), so SHRINK
  and X2 are tested against the true reference, not a straw man.
- SHRINK and X2 are both pre-registered here, before any fitting:
  SHRINK per the template's explicit G-J2-lesson sanction, X2 as
  this league's F4-measured feature. With 14 new clubs every season
  (35% churn — the heaviest in the program), season openers are
  where an unmodified DC is most exposed — the two arms attack that
  exposure from opposite sides (shrink the thin-data rating; inform
  the mover's prior from its tier step). The LaLiga2 step is
  defence-led (F4), the mirror image of ENGCH's attack-led Premier
  League step.
- Halves presentation (goals only): FT + 1H/2H via the frozen
  constant 0.4301, presentation only, exactly as J1.
- Play-off rounds are ordinary rows in every fit (PREPROCESSING
  rule 3); no phase feature is used anywhere. Awarded and
  extra-time scores are used as-is (DATA_UNDERSTANDING §3).
- Predictions-only: no ES-PrimeraFederacion odds/settlement source
  in-system.
