# Step 1 — Data understanding: Tanzania Premier League

## 0 Integrity headline

The warehouse contains 1,284 index rows, 1,284 files, and 1,284 unique match IDs; all 1,284 scores parse. Payload identity agrees with the index on 1,284/1,284, payload dates agree on 1,284/1,284, and header scores agree on 1,284/1,284. The payload parent league is 9066 in 1,284/1,284 records and Tournament parent ID is also 9066 in 1,284/1,284.

There are 2,845 goals in the parsed index/header scores but 2,838 Goal events. This is a measured discrepancy against the coordinator headline of 2,838 total goals; it is not overwritten. Goal-event home/away counts reproduce the index score in 1,281/1,284 rows. Exceptions are `3726033` (AW 3–0 with no events), `4288438` (index 2–0 with no matching Goal events), and `4950929` (index/header 0–3, but one Goal event at 6', home-side event count 1–0). The index/header score is used for targets; event feeds are used only for event coverage and HT extraction.

## 1 Payload anatomy

| Section | Measured content | Use |
|---|---|---|
| `general` / `header` | present in 1,284/1,284; team IDs, names, status and score | identity, status, score cross-check |
| `content.matchFacts.events.events` | 1,147 matches with events; 2,294 Half, 2,838 Goal, 114 Card events | HT and event audit |
| `content.stats` | null in 1,284/1,284 | no SOT/corners/xG/card stats |
| `content.shotmap.shots` | empty in 1,284/1,284 | no shot or xG data |
| `content.playerStats` | null in 1,284/1,284 | no player features |
| `content.lineup` | 10 non-null blocks, all unavailable/zero starters | no lineup feature |
| `infoBox.Referee.text` | non-empty in 0/1,284 | no referee feature |
| `infoBox.Tournament` | present and parent 9066 in 1,284/1,284 | round and single-league check |

## 2 Coverage by season

| Season | rows | eligible | events | HT available | stats | shotmap | lineup blocks | referee |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 240 | 239 | 209 | 209 | 0 | 0 | 0 | 0 |
| 2022/2023 | 240 | 240 | 227 | 227 | 0 | 0 | 0 | 0 |
| 2023/2024 | 240 | 240 | 202 | 202 | 0 | 0 | 0 | 0 |
| 2024/2025 | 240 | 240 | 218 | 218 | 0 | 0 | 0 | 0 |
| 2025/2026 | 240 | 239 | 210 | 210 | 0 | 0 | 10 | 0 |
| 2026/2027 partial | 84 | 84 | 81 | 81 | 0 | 0 | 0 | 0 |

The 1,147 HT values are all from a Half event at time 45. After excluding AW rows, 1,146 are trusted. The raw event count includes the AW match `4950929`; it is never eligible for halves work.

## 3 Calendar and format

This is one pooled single-table league: parentLeagueId 9066 equals league ID 9066. It has 16 teams, 30 rounds, and 240 matches per full season. The first five seasons are complete; 2026/2027 has 84 matches through 2026-11-03. There are 26 distinct team names across the corpus.

## 4 Targets absent

Stats, shotmap, playerStats, usable lineups and referee text provide no modelling targets or covariates. SOT, corners, total shots, xG and yellow cards are absent. Cards are dismissals only: 114 events comprise Red 99, YellowRed 15, and plain Yellow 0.

## 5 Quirks and exceptions

- Explicit AW rows, excluded from every fit, score and halves calculation: `3726033` (2021/2022, Namungo FC–Mbeya Kwanza FC, 3–0) and `4950929` (2025/2026, Dodoma Jiji FC–Pamba Jiji, 0–3).
- The payload status AW rule and the eventless 3–0/0–3 inference agree on 1,283/1,284 rows; the only disagreement is `4950929`, which was played then awarded. Its Half event is 1–0, exceeding the recorded 0–3 FT score; it is the only such match and is flagged `ht_suspect=1`.
- Name-keyed renames are not merged: Singida Big Stars played 29 matches in 2022/2023 and Fountain Gate FC one; Ihefu FC played 28 in 2023/2024 and Singida Black Stars two.
- Movers by season are saved in `inventory_summary.json`; the new/out sets reproduce the supplied list.

All raw counts and every exception list are in `inventory_summary.json`.
