# Phase 1 — Data Understanding: FotMob Austria 2. Liga Warehouse

Corpus: `data_enrichment/fotmob_world/Austria/2. Liga/` — 1,266 full
matchDetails JSONs (FotMob league_id 119), seasons 2021/2022 →
2026/2027, filtered from `data_enrichment/fotmob_world_index.csv`.
Every number below was measured on the files / the Phase-2 CSV, not
taken from index flags (the index's `has_stats` flag is wrong for 12
matches — see quirk 2 — and its `has_period_splits` flag is False
everywhere, which for once matches the content).

## 0. Integrity headline

- 1,266 index rows = 1,266 files = 1,266 CSV rows; match ids unique.
- Goal events reproduce `scoreStr` in **1,265/1,266** matches. The one
  exception is match 4525679 (SW Bregenz 3–0 FC Liefering,
  2024/2025): the events feed records only 2 of the 3 home goals.
  `scoreStr` stays the source of truth; that match's event-derived
  HT split may be short one goal (recorded, not repaired).

## 1. Format — a single-phase second tier with B-teams (read before any window logic)

The 2. Liga is a **single regular phase, double round-robin, no
split, no play-offs** in every season of this corpus (`phase =
regular` on every row; rounds 1–30).

| Season | Teams | Matches | Note |
|---|---|---|---|
| 2021/2022 | 16 | 240 | full |
| 2022/2023 | 16 | 240 | full |
| 2023/2024 | 16 | 240 | full (12 matches lack the stats feed) |
| 2024/2025 | 16 | 240 | full (shot/SOT feed definition break — quirk 3) |
| 2025/2026 | 15 | 210 | full — the virgin season; 15 teams (one club fewer; double round-robin with byes = 210) |
| 2026/2027 | 16 | 96 | **in progress** (rounds 1–12 at pull) — reserved confirmatory window, never read by any gate in this build |

**B-teams.** Five reserve sides of Bundesliga clubs appear, keyed by
FotMob team id: FC Liefering (1915, RB Salzburg II — present all six
seasons), Sturm Graz II (1921, from 2022/2023), Rapid Wien II (1952,
absent 2023/2024), Austria Wien II (10248, absent 2023/2024–
2024/2025), FC Juniors OÖ (292054, LASK juniors, 2021/2022 only).
B-teams are **non-promotable**: they can be relegated to the
Regionalliga (three of the five have been) but can never enter the
Bundesliga, so they never appear as upward movers in any tier-offset
measurement. Entrant classes into this tier are defined in EDA F4
from what actually enters: relegated Bundesliga senior clubs,
promoted Regionalliga senior clubs, returning clubs, and returning
B-teams (from the Regionalliga).

**Team identity** is stable by FotMob team id (27 ids). Names are
display only and vary for the same id (e.g. 10248 "Austria Wien II";
946908 "SPG HOGO Wels" / "FC Hertha Wels"; 10053 "Admira Moedling" /
"Admira Mödling" / "Admira Wacker"; 1907 umlaut variants).

## 2. Coverage matrix (share of matches with real content)

| Season | n | FT stats (4 keys) | Events | Period splits | Shotmap / xG | Referee named |
|---|---|---|---|---|---|---|
| 2021/2022 | 240 | 240 | 240 | 0 | 0 | 0 |
| 2022/2023 | 240 | 240 | 240 | 0 | 0 | 0 |
| 2023/2024 | 240 | 228 | 240 | 0 | 0 | 0 |
| 2024/2025 | 240 | 240 | 240 | 0 | 0 | 0 |
| 2025/2026 | 210 | 210 | 210 | 0 | 0 | 0 |
| 2026/2027 (partial) | 96 | 96 | 96 | 0 | 0 | 0 |

This is a **thin feed**, the opposite of the parent tier's corpus:

- The stats feed carries exactly four keys — `BallPossesion`,
  `total_shots`, `ShotsOnTarget`, `corners` — in `Periods.All` only.
  There is **no** `FirstHalf`/`SecondHalf` block in any payload, no
  xG of any kind, no set-play splits, no `big_chance`, no
  `touches_opp_box`, no `fouls`, and **no `yellow_cards` key** (the
  stats-vs-events cards question is therefore moot here — see
  PREPROCESSING rule 6).
- The **events feed is complete** (1,266/1,266): goals, cards and
  substitutions with times. It is the source for HT goals, the
  cards target and both halves constants.
- The **shotmap is empty in every payload** (0 shots in 1,266
  matches) — no xG, xGOT or shot-quality feature can exist.
- **Referee text is empty in 1,266/1,266 payloads** — the referee
  feature family is dead on arrival in this league.

## 3. Quirk register

1. **Thin feed** (above) — the league's defining constraint. Goals
   are a goals-only Dixon-Coles problem; count markets key on the
   four stats keys plus event yellows.
2. **12 matches in 2023/2024 lack the stats feed entirely** (all
   played, all with scores and full events; concentrated in SW
   Bregenz / SV Ried home fixtures). The index flags exactly these
   12 as `has_stats=False`. Their goals and cards targets exist;
   their SOT / corners / total-shots targets are missing (NaN,
   never zero) and those matches are simply not scored by the
   S/C/T harnesses. Dev stats n is therefore 708, not 720.
3. **Shot/SOT feed definition break in 2024/2025 (and partially
   2026/2027).** Median total shots per match: 18, 18, 17 in
   2021/2022–2023/2024; **22 in 2024/2025**; 16 in 2025/2026; **22 in
   2026/2027**. Median SOT: 9, 9, 8; **11.5 in 2024/2025**; 8 in
   2025/2026; 9 in 2026/2027. Mean SOT/shots ratio: 0.49–0.50 in the
   clean seasons, **0.576 in 2024/2025**, 0.417 in 2026/2027. The
   feed plainly changed what it counts in 2024/2025 (both series
   jump; ratio jumps), the virgin season 2025/2026 sits back in the
   original definition, and 2026/2027 mixes an inflated shots count
   with a reverted SOT count. This is a feed artefact, not football:
   Austrian second-tier teams did not take 30% more shots for one
   season. Consequences, stated plainly: the S-AT2 and T-AT2 dev
   windows contain one contaminated season of three, and their
   trailing state entering the virgin season is partly priced in
   the contaminated definition. No window surgery is done — the
   windows follow the program's season structure and the gates
   judge the result — but any S/T verdict in this league carries
   this caveat in writing.
4. **One goal-event mismatch** (match 4525679, §0).
5. **2025/2026 has 15 teams, not 16** (210 matches). Windows are
   season-blocked, so this needs no adjustment; it is recorded so
   the virgin n=210 is never mistaken for missing data.
6. **2026/2027 is partial** (96 matches) and reserved.
7. **Red cards are frequent** (0.22–0.28/match from events). They
   stay excluded as a target (production cards design); event
   yellows (Yellow + YellowRed) are the cards target.

## 4. Definition alignment

| Concept | Source | Alignment |
|---|---|---|
| FT score | `header.status.scoreStr` | source of truth; events reproduce it 1,265/1,266 |
| HT score | goal events (`time ≤ 45`, credited side) | only halves source for goals; available 1,266/1,266 |
| SOT | stats feed `ShotsOnTarget` | source of record where present (1,254 matches); definition break in 2024/2025 (quirk 3) |
| Total shots | stats feed `total_shots` | source of record where present; same break |
| Corners | stats feed `corners` | source of record where present |
| Yellows | **events feed** (Yellow + YellowRed per team) | stats feed carries no cards key at all — no stats target exists to disagree; `cards_source='events'` on all 1,266 rows |
| Possession | stats feed `BallPossesion` | the only territorial covariate the feed offers |
