# France Ligue 2 — DATA UNDERSTANDING

Source: French FotMob warehouse JSONs indexed under league_id 110. Counts and coverage below are computed from the builder output.

## 2021/2022

- Played matches: 380; teams: 20; rounds: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38.
- Coverage: stats 99.7%, period splits 0.0%, shotmap 0.3%, expected_goals 0.3%, referee 50.0%, events 100.0%.
- Phase counts: {'regular': 380, 'playoff': 0}.

## 2022/2023

- Played matches: 380; teams: 20; rounds: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38.
- Coverage: stats 100.0%, period splits 32.1%, shotmap 0.8%, expected_goals 0.8%, referee 100.0%, events 100.0%.
- Phase counts: {'regular': 380, 'playoff': 0}.

## 2023/2024

- Played matches: 379; teams: 20; rounds: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38.
- Coverage: stats 100.0%, period splits 100.0%, shotmap 0.0%, expected_goals 0.0%, referee 99.7%, events 100.0%.
- Phase counts: {'regular': 379, 'playoff': 0}.

## 2024/2025

- Played matches: 306; teams: 18; rounds: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34.
- Coverage: stats 100.0%, period splits 100.0%, shotmap 1.6%, expected_goals 1.6%, referee 96.7%, events 100.0%.
- Phase counts: {'regular': 306, 'playoff': 0}.

## 2025/2026

- Played matches: 306; teams: 18; rounds: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34.
- Coverage: stats 100.0%, period splits 100.0%, shotmap 100.0%, expected_goals 100.0%, referee 82.7%, events 100.0%.
- Phase counts: {'regular': 306, 'playoff': 0}.

## 2026/2027

- Played matches: 108; teams: 18; rounds: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12.
- Coverage: stats 100.0%, period splits 100.0%, shotmap 100.0%, expected_goals 100.0%, referee 100.0%, events 100.0%.
- Phase counts: {'regular': 108, 'playoff': 0}.

Observed feed rounds are numeric 1–38 only; no promotion play-off or relegation play-out rows are present in this warehouse slice. The team count falls from 20 to 18 in 2024/2025.

## Coordinator addendum (2026-11-09, verified directly from the warehouse)

The promotion/relegation play-off matches involving Ligue 2 clubs DO
exist in the warehouse, but they are filed under Ligue 1: 15 JSONs in
the `France/Ligue 2/` season folders carry `leagueId 53 /
parentLeagueId 110` (e.g. 2023/2024: Saint-Étienne–Metz ×2, Metz–
Saint-Étienne ×1) and are NOT rows of the league_id-110 index. The
frozen phase rule therefore stands as built: the Ligue 2 corpus is
the regular season only; play-off matches are out of scope for every
candidate (they belong to the Ligue 1 slice). This also explains the
21st "team" seen in a naive directory scan of 2023/2024.

## CORRECTION to the addendum above (coordinator, 2026-11-09, verified by full recursive scan)

The addendum's mechanism was WRONG. A complete recursive scan of the
France warehouse tree (5,197 JSONs) finds **zero** files with
`leagueId 53 / parentLeagueId 110` and **zero** non-numeric
`matchRound` values anywhere. The Ligue 1/Ligue 2 promotion play-off
matches (e.g. Saint-Étienne–Metz, June 2024) are simply **absent
from the warehouse entirely** — they are not filed under Ligue 1
either. The frozen phase rule and every downstream result are
unaffected: the Ligue 2 corpus is the regular season only, because
that is all the warehouse holds. The addendum text above is kept
for the record; this correction supersedes it. (The erroneous claim
came from a background scan result the coordinator failed to verify
before committing — recorded plainly as a coordinator defect.)
