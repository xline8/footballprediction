# Phase 1 — Data Understanding: South Korea K League 2

Corpus: FotMob World Warehouse, index filtered to `league_id=9116`.
Measured corpus: 1,407 finished matches (all rows finished). K League 2
runs calendar-year seasons (late Feb/Mar to Nov). Team count grew across
the window: 10 (2021), 11 (2022), 13 (2023–2024), 14 (2025), 17 (2026,
expansion). Team name/ID mapping is perfectly stable: no ID carries two
names and no name carries two IDs (23 team IDs in total).

| Season | regular | play-off | stats block | period splits | events | referee | shotmap | xG in stats | box touches |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021 | 180 | 2 | 0 (0%) | 0 | 180 (100%) | 0 (0%) | 0 | 0 | 0 |
| 2022 | 220 | 2 | 219 (99.5%) | 16 (7.3%) | 204 (92.7%) | 23 (10.5%) | 0 | 0 | 56 (25.5%) |
| 2023 | 234 | 2 | 232 (99.1%) | 208 (88.9%) | 214 (91.5%) | 121 (51.7%) | 0 | 0 | 89 (38.0%) |
| 2024 | 234 | 2 | 229 (97.9%) | 229 (97.9%) | 216 (92.3%) | 86 (36.8%) | 0 | 0 | 229 (97.9%) |
| 2025 | 273 | 2 | 273 (100%) | 273 (100%) | 249 (91.2%) | 80 (29.3%) | 0 | 0 | 273 (100%) |
| 2026 | 256 | 0 | 247 (96.5%) | 247 (96.5%) | 256 (100%) | 90 (35.2%) | 0 | 0 | 247 (96.5%) |

Format and the play-off rule. Each season 2021–2025 ends with two
intra-K2 promotion play-off matches (rounds labelled `1/2` and `final`,
`general.leagueName = "K-League 2 Playoff"`, a distinct sub-league id).
Both clubs are K2 clubs; the cross-tier promotion/relegation ties
against K League 1 clubs are a separate competition and do NOT appear
in this feed at all (verified: the only non-regular rows are these 10).
These knockout rows are a different population (single-match ties,
10 rows total) and are FROZEN OUT of every modelling population; they
are retained in the CSV with `phase=playoff`. Regular rounds are
numbered (36 in 2021, 44 in 2022, 39 in 2023–2025); there is no split
round. 2026 is IN PROGRESS: 256 played, rounds 1–32 only, last match
2026-11-08, play-offs not yet played — it is reserved as confirmatory
data, exactly as KR-KLeague1 reserved its 2026.

Stats gaps, exactly. The 189 stats-less rows are: ALL 182 of 2021 (no
stats block at all); 2022 match 3817257 (1); 2023 matches 4112204,
4112235 (2); 2024 matches 4404849, 4404862, 4404882, 4404909, 4404910
(5; four have no stats block, one has an `All: null` placeholder); plus
9 in reserved 2026. So the stats-target era is 2022–2025 with 8 missing
rows inside it, and 2025 (the virgin) is complete.

xG and shotmap are absent in EVERY season (0 of 1,407): the stats block
never carries `expected_goals` and the shotmap is always empty. Goals
modelling is therefore Dixon-Coles on goals only; every xG-based
template feature is data-absent here (see FEATURES.md).

Two card-feed artefacts (checked before freezing the target):

1. Event feed omits plain yellows in 2022–2025. Total event-feed plain
   `Yellow` card events in the whole corpus by season: 2021: 650,
   2022: 0, 2023: 0, 2024: 0, 2025: 0, 2026: 964. In 2022–2025 the
   event feed carries only Red / YellowRed card events. An
   event-unified yellow target (the KR-KLeague1 construction) is
   therefore IMPOSSIBLE in this league; the stats feed is the only
   yellow source for 2022–2025.
2. Stats yellows are artefact-low in 2022. Stats-feed yellow totals:
   69.4% of 2022 matches record zero yellows (monthly means 0.6–1.4
   until Oct 2022: 3.12), versus 10.3% zero matches and mean 2.93 in
   2023. The Feb–Sep 2022 stats yellow recording is broken (missing
   recorded as zero). The cards population is therefore frozen to
   2023–2025 (see PREREG_K_KR2); 2022 is excluded from cards entirely,
   2021 has no stats at all.

Frozen windows: goals dev seed 2021, scored 2022–2024 (688); stats
markets dev seed 2022, scored 2023–2024 (461 with target); cards dev
seed 2023, scored 2024 (229 with target); virgin = complete 2025 (273
regular) for every candidate; 2026 reserved, not read in this build.
