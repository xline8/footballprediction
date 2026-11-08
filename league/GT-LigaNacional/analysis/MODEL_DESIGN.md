# Model design and feasibility

This phase performs no fitting. The intended boundary is seed 2021/2022;
development 2022/2023–2024/2025 (pooled n=746); virgin 2025/2026 complete
(n=292); and 2026/2027 reserved confirmatory data (n=113, in progress).
Descriptive EDA uses all six seasons, but no model purpose may read virgin or
confirmatory data during Phase A.

| target | measured source | verdict | reason |
|---|---:|---|---|
| Goals | 1,443/1,443 | **BUILDABLE** | Header scores are present in every finished match. |
| SOT | 0/1,443 | **NOT BUILDABLE** | Stats is `None` everywhere and shotmaps have zero shots. |
| Corners | 0/1,443 | **NOT BUILDABLE** | No stats feed exists. |
| Cards | 0 yellow-card observations; 570 dismissal events | **NOT BUILDABLE** | The event feed has only Red/YellowRed; no valid target or stats validation. |
| Total shots | 0/1,443 | **NOT BUILDABLE** | No stats feed and no shotmap shots. |

## G-GT candidate sketch

Dixon–Coles goals-only. The reference architecture is seeded on 2021/2022,
uses the three-season development pool above, and reserves complete 2025/26
as virgin plus 2026/27 as confirmatory. Primary line: OU2.5. Presentation is
FT-only and `halves_constants` remains `{}`.

The two authorized arms are Gate Zero and SHRINK. SHRINK scales attack and
defence ratings toward league mean by n/6 for teams with fewer than six prior
in-league matches; n=0 remains the unseen-team default. There is no X2 mover
arm and no count-market fit is authorized.

The later fitting phase may create `engine/goals/`, development and virgin
results, fitted virgin parameters, PASS-only predictions, and
`reports/G_GT_VERDICT.md`. Those artifacts are intentionally absent here
because Phase A forbids fitting.
