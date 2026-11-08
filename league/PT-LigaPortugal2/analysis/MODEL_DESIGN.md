# Model design and feasibility

This phase performs no fitting. The feasibility matrix is based on content
measurements and the frozen windows: seed 2021/2022; development seasons
2022/2023, 2023/2024, 2024/2025 (pooled n=918); virgin 2025/2026 complete
(n=306); and 2026/2027 (n=89) reserved as confirmatory and not read by a
future model build.

| target | source exists | multiple eras for blocked dev | virgin contains target | verdict |
|---|---:|---:|---:|---|
| Goals | 1,619/1,619 | yes | yes | **BUILDABLE** |
| SOT | 396 matches, 2024/25 partial + 2025/26 full | no | yes | **NOT BUILDABLE** |
| Corners | 396 matches, 2024/25 partial + 2025/26 full | no | yes | **NOT BUILDABLE** |
| Cards via stats | 0/1,619 | no | no stats target | **NOT BUILDABLE** |
| Cards via events | event Card in 113, 83, 62, 140, and 303 matches in the five pre-confirmatory seasons respectively | events occur in multiple seasons, but event schema/coverage is unstable and no stats-yellow overlap validates the target | yes | **NOT BUILDABLE** |
| Total shots | 396 matches, 2024/25 partial + 2025/26 full | no | yes | **NOT BUILDABLE** |

The 90-match partial stats block is not a separate season era capable of
supporting a blocked dev evaluation. Card events do occur in several
development seasons, contrary to the initial expectation, but their
coverage and yellow/red semantics are not stable and the requested
stats-vs-events validation sample is empty. Counts are therefore
documentation-only until a future pull supplies a stable target source and
validation overlap.

## G-PT2 candidate

The candidate is Dixon–Coles goals-only, following the BG production pattern:
14 multiplicative sweeps, damping 0.7, +0.25 smoothing, fitted home
advantage initialized at 0.28, rho grid `(0, -0.05, -0.10, -0.15)` selected by
weighted goals log likelihood, `MAXG=10`, production tau correction, and
270-day decay half-life. Fits are expanding and season-blocked; unseen teams
start at the league mean.

Arms are Gate Zero and SHRINK. SHRINK scales attack and defence ratings by
`n/6` at prediction time for teams with fewer than six prior in-league
matches. There is no mover arm. The primary line is OU2.5; baselines are
prior-season pooled climatology. Development is evaluated on 2022/23,
2023/24, and 2024/25 (pooled 918); the virgin is 2025/26 (306), read once
only for dev-passing arms. The 2026/27 pull is reserved confirmatory data.

All predictions are FT-only because no halves constant is frozen. A future
goals build may use the event-derived 1H share only if it explicitly freezes
that constant under a new approved design decision; this phase does not.
