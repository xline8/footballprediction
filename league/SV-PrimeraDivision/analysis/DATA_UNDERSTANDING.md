# Step 1 — Data Understanding: El Salvador Primera Division (FotMob 335)

Corpus: `data_enrichment/fotmob_world/El Salvador/Primera Division/` —
1,448 matchDetails JSONs, tournaments 2021/2022 Apertura → 2026/2027
Apertura, one tier. Inventory tool: the content scan in
`analysis/eda_numbers.py` (raw results in
`analysis/inventory_summary.json`). Every number below was measured
on the files, never taken from the index's `has_*` flags — which are
all `False` here anyway and, per program experience, test key
presence, not non-null content.

## 0. Integrity headline

- 1,448 index rows = 1,448 files on disk = 1,448 unique match ids. No
  duplicates, nothing on disk missing from the index, nothing in the
  index missing on disk. All scores parse (`score` present on all
  1,448 rows).
- `header.teams[].score` equals the index `score` on **1,448/1,448**.
  Goal-event counts reproduce the index score on 1,333/1,334
  event-bearing matches (the single exception is the duplicate-goal
  event in §5 — the header/index score is the source of truth).

## 1. Payload anatomy (one matchDetails JSON)

| Section | Contents | Modelling relevance |
|---|---|---|
| `general` | matchId, leagueId (the tournament sub-id, e.g. 874467), leagueName ("Primera Division - Apertura"), parentLeagueId 335, matchRound, team ids/names | identity, tournament/round structure |
| `header.teams` | home/away team **ids + names + scores** | FT score, team identity (ids) |
| `header.status` | utcTime, red-card counts, half timestamps | kickoff, anomaly flags |
| `content.matchFacts.events.events` | Goal (scorer, `isHome`, minute, `newScore`), Card (`card` ∈ Red/YellowRed only — see §4), Half (time 45/90, **with `homeScore`/`awayScore` at HT**) | HT derivation, dismissals |
| `content.matchFacts.infoBox` | Match Date, Tournament (id, parentLeagueId 335, round), Stadium, Referee (key present, **text always empty**), Attendance (null) | round, no usable referee/stadium data |
| `content.stats` | key present; `Periods` blocks carry **no stat rows in any payload** | SOT/corners/cards/xG targets: absent |
| `content.shotmap.shots` | key present; **empty list in every payload** | no per-shot data |
| `content.lineup`, `content.playerStats` | keys present; lineup block **absent in all 1,448 payloads** (no block at all, not even an empty one); playerStats empty everywhere | no lineup/player data |
| `content.table`, `h2h`, `momentum` | standings snapshot, head-to-head, momentum flag | not used (post-match snapshots; leakage risk) |

## 2. Coverage matrix (share of matches with real content, %)

| Tournament | n | Stats (non-empty) | Shotmap (shots>0) | Events | HT score | Lineups (starters) | Player stats | Referee (non-empty text) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021/2022 - Apertura | 145 | **0** | **0** | 95.2 | 95.2 | 0 | 0 | **0** |
| 2021/2022 - Clausura | 145 | **0** | **0** | 91.7 | 91.7 | 0 | 0 | **0** |
| 2022/2023 - Apertura | 80 | **0** | **0** | 91.3 | 91.3 | 0 | 0 | **0** |
| 2022/2023 - Clausura | 137 | **0** | **0** | 93.4 | 93.4 | 0 | 0 | **0** |
| 2023/2024 - Apertura | 145 | **0** | **0** | 92.4 | 92.4 | 0 | 0 | **0** |
| 2023/2024 - Clausura | 145 | **0** | **0** | 89.7 | 89.7 | 0 | 0 | **0** |
| 2024/2025 - Apertura | 123 | **0** | **0** | 92.7 | 92.7 | 0 | 0 | **0** |
| 2024/2025 - Clausura | 123 | **0** | **0** | 87.0 | 87.0 | 0 | 0 | **0** |
| 2025/2026 - Apertura | 145 | **0** | **0** | 93.1 | 93.1 | 0 | 0 | **0** |
| 2025/2026 - Clausura | 145 | **0** | **0** | 95.2 | 95.2 | 0 | 0 | **0** |
| 2026/2027 - Apertura (partial) | 115 | **0** | **0** | 90.4 | 90.4 | 0 | 0 | **0** |
| **Total** | **1,448** | **0** | **0** | **92.1** | **92.1** | **0** | **0** | **0** |

Reading of the matrix:

- **El Salvador is a scores-only corpus, cleanly.** No tournament
  has any stats, shotmap, player-stat, referee or lineup content at
  all. The `has_stats`/`has_shotmap` index flags are `False` for all
  1,448 rows and the payloads confirm it by content.
- Events exist in 1,334/1,448 matches (92.1%). The 114 matches
  without events split exactly two ways (measured, §5): 112 are
  0-0 draws (played, goalless) and 2 are non-0-0 played matches
  whose event feed is missing. No event-less match is a forfeit:
  there is no team-concentrated 3-0 pattern of the Ghana kind, and
  both non-0-0 cases are isolated (different tournaments, both
  Santa Tecla away wins).
- HT scores are directly readable from the Half event at time 45
  (`homeScore`/`awayScore`): 1,334/1,448 matches (92.1%), all of
  them trustworthy (the one event-feed error is a second-half
  duplicate — §5 — and its HT value is verified consistent).

## 3. Format

- **Split seasons: Apertura + Clausura, each a separate FotMob
  sub-league** under parent id 335 (`general.leagueId` differs per
  tournament, e.g. 874467 for 2021/2022 Apertura; `parentLeagueId`
  is 335 on every row). Each tournament: a regular phase (22 rounds,
  double round robin) followed by playoffs (quarter-finals 8
  matches, semi-finals 4, final 1 — 13 total). 12 teams normally;
  **11 teams in both 2024/2025 tournaments** (22 rounds × 5 = 110
  regular matches). Regular-phase counts: 132 per full 12-team
  tournament, 110 per 11-team tournament, 67 for the shortened
  2022/2023 Apertura (see below), 115 so far for the in-progress
  2026/2027 Apertura.
- **Turnover happens only between season-years, never within one:**
  the Clausura always fields exactly the same 12 (or 11) team ids
  as the preceding Apertura (0 new ids in every Clausura). New ids
  per Apertura: 2022/2023: 1 (CD Dragon); 2023/2024: 2 (Municipal
  Limeno returns, Fuerte San Francisco enters); 2024/2025: 1 (CD
  Cacahuatique); 2025/2026: 2 (Inter FA, Zacatecoluca); 2026/2027:
  2 (Atletico Balboa, Inca Aruba). There is no built Salvadoran
  parent/sibling in the warehouse, so no cross-league mover prior
  exists; the SHRINK arm is the thin-data treatment (MODEL_DESIGN
  §2).
- Calendar: Apertura Jul–Dec, Clausura Jan–May. Tournament date
  ranges: 2021/2022 Apertura 2021-08-01→2021-12-19; 2021/2022
  Clausura 2022-01-16→2022-05-29; 2022/2023 Apertura
  2022-07-09→2022-11-13; 2022/2023 Clausura 2023-01-28→2023-05-20;
  2023/2024 Apertura 2023-08-13→2023-12-24; 2023/2024 Clausura
  2024-01-14→2024-05-26; 2024/2025 Apertura 2024-07-27→2024-12-22;
  2024/2025 Clausura 2025-01-19→2025-05-25; 2025/2026 Apertura
  2025-07-20→2025-12-21; 2025/2026 Clausura 2026-01-17→2026-05-24;
  2026/2027 Apertura 2026-07-25→2026-11-09 (in progress, rounds
  1–19 + one round-21 match).
- Team identity is by **FotMob team id** (`header.teams[].id`): 19
  distinct ids across the corpus, 12 (11) per tournament, no id
  maps to two clubs. Three ids carry two name spellings: one genuine
  rename (49747 Once Deportivo → Hercules) and two variants
  (49739 CD Águila / CD Aguila — diacritic; 1783449 Inter Santa
  Tecla / Inter FA). Keying on names would split three clubs in
  two (and the 2023/2024 Clausura would appear to have 13 teams);
  keying on ids is exact.

## 4. Cards: why K is not buildable

- The 593 Card events are **all dismissals**: Red 449, YellowRed
  144, **0 plain Yellow events in 1,448 payloads**. No stats
  yellows exist either (stats empty). There is therefore **no
  yellow-card target** in any form — neither a stats feed nor an
  event feed — in any tournament. K-SV is NOT BUILDABLE
  (payload-level evidence in
  `prereg/PREREG_SCKT_SV_NOT_BUILDABLE.md`).
- Referee identity is empty in all 1,448 payloads
  (`infoBox.Referee` key present, `text` always `''`), so X8 has
  no input even if a target existed. Dismissals themselves
  (0.41/match) are a rare event with no reliability evidence and
  are not a target.

## 5. Anomalies (frozen handling in PREPROCESSING.md)

| match | tournament | issue | handling |
|---|---|---|---|
| 4708064 Isidro Metapan vs Once Deportivo | 2024/2025 - Clausura, round 2, 2025-01-26 | **Duplicate goal event**: the same goal (eventId 12333271, Marvin Monterrosa 67') appears twice, `newScore` [3,1] then [4,1]. Event FT score (4-1) disagrees with the official header/index score (3-1). HT (2-1) is consistent with the first three goal events | FT score from header/index (official); flagged `event_ft_mismatch=1`; HT kept (verified consistent, `ht_suspect=0`) |
| 3677630 Firpo vs Santa Tecla FC | 2021/2022 - Apertura, round 10, 2021-09-19 | **Event feed absent for a played match with goals** (0-2) | FT score from header/index; HT missing (null); stays eligible |
| 4397305 Jocoro FC vs Santa Tecla FC | 2023/2024 - Clausura, round 11, 2024-03-16 | **Event feed absent for a played match with goals** (0-3) | FT score from header/index; HT missing (null); stays eligible |
| 2022/2023 - Apertura | 2022/2023 - Apertura | **Shortened regular phase**: rounds 1–10 only (67 matches). Round "1" carries 12 matches in two batches (6 on 2022-07-09/10, 6 on 2022-09-17/18); round "2" similarly split (Jul + Sep 2022). Full playoffs (13) follow | Recorded as observed; the 67 regular matches enter the fit as ordinary results |
| 2022/2023 - Clausura | 2022/2023 - Clausura | **Playoffs stop after 5 QF matches** (last match 2023-05-20, CD Dragon–Firpo 2-1); no semi-finals or final in the warehouse | Recorded as observed; the 5 QF matches are playoff rows, excluded from fit/score like all playoffs |
| 2026/2027 - Apertura | 2026/2027 - Apertura | **In progress**: rounds 1–19 complete (6 each) + one round-"21" match (Municipal Limeno–Fuerte San Francisco 1-1, 2026-11-05); rounds 20/22 not yet played | Reserved confirmatory window; not part of this build |

Total excluded from every fit/score/EDA level: **0 rows** — there are
no awarded/forfeit rows in this league. All 1,448 rows are eligible;
the playoff rows (122) are excluded from fit/score/EDA levels by the
regular-phase-only rule, not by eligibility.

## 6. What does not exist here (explicit)

- No xG (of any kind), no SOT, no corners, no total shots, no cards
  target, no referee, no player data, no lineups (no lineup block
  exists in any payload), no substitutions, no stadium, no
  attendance, no team-name-only identity problem — in **any**
  tournament. S/C/K/T are not buildable (see MODEL_DESIGN §1). No
  proxy is constructed for any of them.
