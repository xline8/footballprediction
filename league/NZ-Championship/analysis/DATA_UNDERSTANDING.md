# Data understanding — NZ-Championship

The re-checked index has 229 rows for FotMob league 8870, dated
2022-10-01 through 2026-11-08. Seasons are calendar-year labels. The
built files contain 38, 46, 46, 56 and 35 PLAYED matches for
2022–2026: the index holds 229 rows but eight 2022 rows are scheduled
fixtures that were never played (see below), so the analysis corpus is
221 matches.

The format is a single round robin plus one final per season: 10 teams
and rounds 1–9 (45 matches) + final in 2022–2024; 11 teams and rounds
1–11 (55 matches) + final in 2025–2026. 2026 is in progress (rounds
1–7, 35 matches, no final yet). The 2025 jump from 46 to 56 matches is
the 11th team, not a new playoff phase. The final's `leagueName` in
2022 reads "National League Final Stage" (match 4070029) versus
"National League Championship" elsewhere; the phase rule keys on
`leagueRoundName == "final"`, so this is cosmetic.

## The eight unplayed 2022 fixtures

Index rows `4024974, 4024976, 4024979, 4024955, 4024963, 4024987,
4024984, 4024988` (rounds 2, 2, 3, 4, 6, 7, 7, 8) have
`header.status.finished = false`, `started = false`, empty `halfs`,
and `scoreStr = null`, while the index `score` column carries a `0-0`
placeholder. They were never played and never replayed under another
match id (no duplicate pairings exist among played matches), so the
2022 round robin is genuinely incomplete: Miramar Rangers played only
5 matches, Wellington Olympic 10 (9 rounds + final), the other eight
clubs 7–8. The builder excludes them under the frozen
finished/non-cancelled rule; their ids are listed here so a future
warehouse refresh that completes them is detectable (the builder's
season-count assertion would fail loudly).

## Coverage

On the 221 played matches: score 221/221, events 178/221, stats
0/221, period splits 0/221, named referees 0/221, shotmaps/xG 0/221
in content terms, lineups 0/221, halfs timestamps 221/221. The event
blackout is the whole of 2022 (0/38); 2023 is 45/46, 2024 45/46, 2025
54/56, 2026 34/35. The five eventless matches outside 2022 are
`4326604` (2023), `4638306` (2024), `4970108, 4970110` (2025),
`6255247` (2026).

Event types across the corpus: Goal 687, Card 34 (Red 27, YellowRed 7,
zero plain Yellow), Half 358, PenaltyShootout 1. The `content.shotmap`
object is present on every payload but always empty
(`{"shots": [], "Periods": {"All": []}}`) — there is no shot data of
any kind, so the index `has_shotmap: False` flag happens to be right
for the wrong reason (key presence, not content).

## Extra-time finals

The 2024 and 2025 finals went to extra time and their recorded scores
include extra-time goals. 2024 final (match 4679973): recorded 1-2,
Goal events at 24' (home), 44' (away), 111' (away) — the 90-minute
score is 1-1. 2025 final (match 5087158): recorded 2-2, Goal events
at 81' (away), 90' (home), 101' (home), 120' (away), then a
PenaltyShootout event — the 90-minute score is 1-1. The 2023 final
was 2-0 inside 90 minutes. The 2022 final has no events, but its
`halfs` timestamps show empty extra-half fields and `gameEnded` ~8
minutes after the second half ended, so it was decided inside 90
minutes and its recorded 3-2 is the 90-minute score. The builder
stores the 90-minute score for every match (see PREPROCESSING.md).

Team identity is stable by FotMob ID (18 distinct ids). The one
published-name variant is 613344: "Eastern Suburbs" in 2023,
"Eastern Suburbs AFC" in 2024/2026. The machine-readable counts and
IDs are in `inventory_summary.json`. There is no other New Zealand
league in the warehouse (verified: distinct (league, league_id) for
country "New Zealand" in the index is only Championship 8870), so no
sibling-league mover prior exists.
