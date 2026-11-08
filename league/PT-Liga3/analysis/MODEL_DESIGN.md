# Model design and feasibility

This phase performs no fitting. The fitting boundary is seed 2021/2022;
development 2022/2023–2024/2025 (pooled n=929); virgin 2025/2026 complete
(n=296); and 2026/2027 (n=90) reserved confirmatory data. Descriptive EDA may
use all seasons, but no model purpose may read virgin or confirmatory data.

| target | source | verdict | reason |
|---|---:|---|---|
| Goals | 1,647/1,647 | **BUILDABLE** | Complete header scores and multiple eras. |
| SOT | 0/1,647 | **NOT BUILDABLE** | `content.stats` is None and shotmaps have zero shots. |
| Corners | 0/1,647 | **NOT BUILDABLE** | No stats feed. |
| Cards | 0 stats; unstable events | **NOT BUILDABLE** | Event coverage breaks by season; stats-vs-events validation n=0. |
| Total shots | 0/1,647 | **NOT BUILDABLE** | No stats feed and no shotmap shots. |

## G-PT3 candidate sketch

Dixon–Coles goals-only, with Gate Zero and SHRINK arms. SHRINK is the PT2
definition: ratings are scaled by n/6 for teams with fewer than six prior
in-league matches. There is no X2 mover arm: direct PT↔PT3 counts are zero and
PT2↔PT3 evidence is only 1–3 clubs per direction per transition, so no frozen
offset is justified. The primary line is OU2.5. Seed 2021/2022; dev
2022/2023–2024/2025 pooled n=929; virgin 2025/2026 n=296; confirmatory
2026/2027 n=90. No model is fitted in Phase A. Outputs are FT-only and
`halves_constants` remains `{}`.
