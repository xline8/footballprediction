# NL Eerste Divisie — exploratory findings

All figures below are descriptive measurements from `eda_summary.json`; no model is fitted and no virgin outcome is used for arm selection.

## F1 — levels and home advantage

| season | goals | SOT | corners | stats cards | event cards | total shots |
|---|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 3.066 | 9.905 | 10.242 | 2.489 | 2.711 | 26.145 |
| 2022/2023 | 3.068 | 9.321 | 9.405 | 3.084 | 3.287 | 25.295 |
| 2023/2024 | 3.050 | 9.566 | 10.284 | 3.213 | 3.268 | 25.889 |
| 2024/2025 | 3.016 | 9.784 | 10.353 | 3.313 | 3.387 | 26.747 |
| 2025/2026 | 3.195 | 10.242 | 10.782 | 3.384 | 3.279 | 28.495 |
| 2026/2027 | 3.525 | 10.331 | 10.576 | 3.266 | 3.295 | 29.446 |

Pooled goals are 3.109 per match and the home-goal minus away-goal mean is 0.324. Pooled levels are descriptive, including 2025/2026 and the partial 2026/2027 season.

## F2 — team-trait reliability

Pooled random split-half r (60 repetitions; teams with at least 24 team rows): goals for/against 0.817/0.691; SOT 0.847/0.866; corners 0.784/0.833; event yellows 0.478/0.471; total shots 0.879/0.915; possession 0.910/0.910; big chances 0.669/0.750; touches in opponent box 0.875/0.918. Season-by-season values are retained under `reliability_by_season` in the JSON; the partial current season is not used to claim production stability.

## F3 — half shares and true variance

Goals from events across all seasons have a 1H share of 0.451 and team split-half r of only 0.075. For the period-split era (2023/2024 onward), SOT/corners/total shots/yellows have 1H shares 0.451/0.462/0.451/0.326 and team split-half r -0.025/0.079/0.244/0.104. COORDINATOR CORRECTION: the first-pass binomial noise floor in the JSON was understated; recomputed per-match (noise = mean of p(1-p)/total_i) the true variances are goals -0.008, SOT -0.001, corners -0.001, total shots +0.0001, yellows +0.014 — i.e. at or below zero for goals/SOT/corners/shots and small-positive only for yellows, with team share reliability near zero throughout. Conclusion unchanged and stronger: these are frozen league constants for reporting, never team features.

## F4 — referee strictness

Referee text is non-empty for 87.35% of all matches, with 32 referees meeting the 20-match descriptive threshold. Card-rate split-half r is 0.420. This is measurable; per program precedent (adopted at r=0.378 in BE/USL with the same coverage shape) X8 is ADOPTED as a gated arm in FEATURES (coordinator correction there); fixtures without a named referee fall back to Gate Zero.

## F5 — movers and X2 evidence

COORDINATOR CORRECTION (verified 2026-11-09 against the built NL-Eredivisie corpus, league id 57 in the same warehouse): the entrant classification in the first-pass JSON is wrong. EVERY entrant in EVERY transition (2022/2023: Heracles, PEC Zwolle, Willem II; 2023/2024: Cambuur, FC Emmen, FC Groningen; 2024/2025: Excelsior, FC Volendam, Vitesse; 2025/2026: Almere City FC, RKC Waalwijk, Willem II; 2026/2027: FC Volendam, Heracles, NAC Breda) played in the Eredivisie in the immediately preceding season — they are RELEGATED clubs. No Tweede Divisie club entered in any observed transition (the Tweede champion did not take promotion in these years). The per-transition first-season gaps (entrant GF/GA per team-match vs that season's league team-goal mean) are: 2022/2023 +0.845/-0.460, 2023/2024 +0.281/-0.090, 2024/2025 +0.390/-0.110, 2025/2026 +0.254/-0.171. Pooled match-weighted over the four complete transitions (n=456 entrant team-matches, recomputed by the coordinator from the CSV): GF gap +0.419, GA gap -0.199.

Reading: relegated Eredivisie clubs enter STRONGER than the Eerste average — the mirror image of the Eredivisie's X2 (promoted clubs enter weaker). X2 is adopted as a relegated-club prior with the pooled magnitudes above, gated like every arm.

## F6 — Jong behavior

The four reserve teams are measured separately. Jong goals-for split-half r is 0.843 versus 0.805 for non-Jong; Jong goals-against r is 0.153 versus 0.644. Jong GF variance is 1.766 versus 1.707 for non-Jong, and GA variance is 1.707 versus 1.709. The defensive reliability contrast is the important result: reserve-team behavior is less stable on goals against, despite similar pooled volatility.

## F7 — missing xG/shotmap and target implications

There is no expected-goals key in any season and only one non-empty shotmap row. xG blend, set-play xG, xG per shot, and xGOT are unavailable. SOT, corners, cards, and total shots remain feasible count targets from stats/events.

## F8 — design boundary

No fitting, preregistration, engine, or virgin read was performed. The complete 2025/2026 levels are included only as the same design-level aggregate allowed in the brief.
