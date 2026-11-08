# Step 1 — Data Understanding: Tunisia Ligue I

Source: FotMob world warehouse, index `data_enrichment/fotmob_world_index.csv`
(filter `league_id == 544`), payloads under
`data_enrichment/fotmob_world/Tunisia/Ligue I/<season>/`.
Inventory: `league/TN-LigueI/analysis/inventory_summary.json`.
Builder: `league/TN-LigueI/data/build_data.py` → `tn_matches.csv`
(1,060 rows, one per played match; 1,051 model rows after the 9
awarded exclusions).

## Identity — one true league, verified from payloads

- `general.parentLeagueId == 544` in ALL 1,060 payloads.
  `general.leagueName` is phase-labelled, not a sub-competition
  marker: "Ligue I" 536, "Ligue I Grp. A" 154, "Ligue I Grp. B" 154,
  "Ligue I Championship Group" 116, "Ligue I Relegation Group" 98,
  "Ligue I Placement Matches" 2 — the group/playoff names are the
  phases of the same competition under parent 544.
- `general.coverageLevel` is "lower" in every payload (the warehouse
  collected scores + events only for this league).

## Seasons and format

| Season | Index rows | Model rows | Format | Status |
|---|---|---|---|---|
| 2021/2022 | 156 | 156 | 2 groups of 8 (112) + Championship 6 (30) + Relegation 4 (12) + Placement 2 | complete |
| 2022/2023 | 198 | 195 | groups 112 + Championship 8 (56) + Relegation 6 (30) | complete (3 awarded) |
| 2023/2024 | 170 | 170 | groups of 7+7 (84) + Championship 6 (30) + Relegation 8 (56) | complete |
| 2024/2025 | 240 | 237 | single table, 16 teams, 30 rounds | complete (3 awarded) |
| 2025/2026 | 240 | 237 | single table, 16 teams, 30 rounds | complete (3 awarded) — virgin |
| 2026/2027 | 56 | 56 | single table, rounds 1–7 | in progress — reserve |

Format history: 2021/22–2023/24 used two groups followed by
championship / relegation groups (double round robin within each
phase); from 2024/25 the league is a single 16-team table, 30
rounds. The 2021/22 Placement Matches are two one-off fixtures
(CA Bizertin–AS Soliman 2-1, US Tataouine–AS Rejiche 5-3, both FT).
2023/24 has only 14 teams: Sportif de Chebba (id 852754) is absent
that season (excluded from the league) and never returns. Calendar:
October/November–May/June in the group era; August–May in the
single-table era.

All phases are league matches with 90-minute scores — no extra time
and no penalty shootout anywhere in the corpus (0 AET Half events,
0 `penaltyShootoutEvents`) — so ALL phases enter the model data.
This is the honest regular-phase treatment: the group +
playoff/championship structure is modelled as it is, with phase
recorded per match, and no split-group exclusion (the DK-2Division
precedent was checked: its split handling is league-specific; here
nothing in the payloads justifies excluding any phase — every phase
is 90-minute league football between the same pool of teams).

## Field coverage per season (from payloads, not index flags)

The index `has_stats` / `has_shotmap` / `has_lineup` /
`has_period_splits` flags are key-presence flags and are False
everywhere here; all coverage below was verified by reading the
1,060 payloads.

| Field | Coverage |
|---|---|
| FT score (`header.teams[].score`) | 1,060/1,060; every payload `finished=True` |
| `content.stats` | null in ALL 1,060 — no stats feed in any season |
| `content.shotmap.shots` | empty list in ALL 1,060 — no shots/xG data |
| xG (`expected_goals*`) | absent everywhere (consequence of stats null) |
| Referee | never named — `infoBox.Referee.text` is "" in all 1,060 payloads |
| Lineup / playerStats | lineup key present in 245 payloads (2025/26+: 201, 2026/27: 42) but never used — no lineup feature is built from it; playerStats empty |
| Events (`matchFacts.events.events`) | present (non-empty) in 925/1,060 matches; 135 matches have an empty events list, of which 133 are 0-0 and 2 are awarded |
| Goal events | 2,005 total; count == header goal total in every NON-awarded match with events (0 mismatches) |
| Half events (`HT`/`FT`) | 1,846 total; HT event present in 925/1,060 matches (the same 925 with events) |
| Card events | 241 total in 216 matches — ONLY Red (227) and YellowRed (14); NO plain Yellow event exists anywhere |

## Quirks (all recorded, none silently patched)

1. **Nine awarded matches** (`header.status.awarded == True`,
   reason `AW`): 4096477, 4145842, 4145834 (2022/23); 4608322,
   4608325, 4612011 (2024/25); 4919136, 4919206, 5178447 (2025/26).
   The header score is a forfeit score (0-2 / 2-0 / 0-3) that
   disagrees with the played event trail — e.g. 5178447 played 3-2
   (5 goal events, trail ending [3,2]) but is recorded 0-2; 4608322
   played 2-2, recorded 0-2; 4145842 played 1-2, recorded 2-0.
   Following the AE-ProLeague precedent, awarded matches are kept
   in the CSV with `is_awarded=1` and are EXCLUDED from every fit,
   every baseline, and every metric. Their halves columns are blank
   (missing, not zero).
2. **Team-name accent variants:** the same FotMob team id appears
   under two spellings — id 8153 "Esperance" / "Espérance", id
   102104 "Olympique de Beja" / "Olympique de Béja", id 405958
   "Etoile Metlaoui" / "Etoile Métlaoui". Team identity is therefore
   keyed by id everywhere; name-based entrant lists would be wrong
   (a naive name comparison "discovers" 3 phantom entrants in
   2023/24 and 2026/27).
3. **No period-split stats:** the only 1H/2H information is the
   goal-event times (and the HT Half-event score, which agrees with
   them in all 925 matches where both exist — 0 disagreements).
   There are no 1H SOT/corner/card splits because those targets do
   not exist at all.
4. **Card feed is fragmentary and red-only:** cards appear in only
   216/1,060 matches (20%), with no yellows at all. A real Ligue I
   match averages ~3–4 cards; 0.23 card events/match means the feed
   records a small, non-random subset (reds only). No cards
   candidate can be built from this.
5. **Two no-events matches with goals** (4145834, 4919206) are both
   awarded; their halves are blank per quirk 1. All other no-events
   matches are 0-0, so their 1H/2H goals are genuinely 0.

## What this league is

A **scores-only league**: FT scores + goal-event times, nothing else.
Only the goals candidate (G-TN) is buildable. SOT, corners, total
shots are not buildable (no stats/shotmap in any season); cards is
not buildable (no yellows; reds only, fragmentary; referee never
named). The goals model is goals-only Dixon-Coles (no xG blend
anywhere).
