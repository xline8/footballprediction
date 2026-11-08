# Phase A — Data Understanding: Saudi First Division

Corpus: 712 finished FotMob matchDetails payloads for league 10721,
covering 2024/2025, 2025/2026, and the first 11 rounds of 2026/2027.
The builder produces 712 unique match rows and 1,424 team-match rows.

## 0. Integrity headline

- 309 / 309 / 94 rows by season; 3 promotion-playoff matches in each
  complete season; no playoffs in the partial season.
- All payloads are finished. There are two awarded matches and no cancelled
  matches: 1000006540 and 1000006697.
- Team identity is keyed by FotMob team id; names are canonicalised to the
  most frequent name observed for each id.

## 1. Format

The league has 18 teams, a 34-round regular phase (306 matches), and a
three-match promotion playoff (two semifinals and a final) in each complete
season. Six teams change at each season boundary. Playoffs are structurally
identified by `matchRound` containing `Play-off` and are excluded from every
fit and scored window. The 2026/2027 corpus is partial through round 11.

## 2. Coverage matrix

| Season | Rows | Stats (all 32 keys) | Stats halves | Events | Lineup | Referee | Shotmap empty |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024/2025 | 309 | 0 | 0 | 0 | 0 | 0 | 309 |
| 2025/2026 | 309 | 307 | 307 | 307 | 309 | 0 | 309 |
| 2026/2027 partial | 94 | 94 | 94 | 94 | 94 | 93 | 94 |

Every one of the 32 requested keys has the same per-period coverage as the
stats count above: 0 / 307 / 94 for All, FirstHalf, and SecondHalf by season.
There is no xG, xGOT, or usable shotmap content anywhere in these 712 files.

The 2024/2025 season is a score-only ghost season: FT scores exist, but stats,
events, lineups, and referees do not. In 2025/2026 the two stats-null matches
are awarded wins (1000006540, 2026-01-21 Al-Faisaly–Abha 3-0; 1000006697,
2026-01-22 Al-Ula FC–Al-Wehda 0-3). Referee coverage exists only in the
in-progress season. No outcome levels are computed for 2026/2027.

## 3. Definition alignment

| Concept | Source / definition |
|---|---|
| FT score | `header.status.scoreStr` |
| HT score | goal events with `time <= 45`; otherwise null, with `ht_source=none` |
| Period stats | `content.stats.Periods`, using the 32-key allowlist |
| Cards target | event Yellow + YellowRed; stats red cards retained as cross-check columns only, never a target |
| Phase | `playoff` iff `matchRound` contains `Play-off`, else `regular` |
| Shotmap | explicitly empty: shot counts are 0 and xG/xGOT are null |

### 3.1 Cards feed check

The check below uses the 307 2025/2026 matches with real stats. Event totals
across all 309 matches are Yellow 1326, Red 50, and YellowRed 39.

| Comparison | Matches |
|---|---:|
| Exact agreement | 259 / 307 |
| Stats-low | 48 |
| Stats-high | 0 |
| Mean (stats − event-unified yellows) | −0.2964 |

The stats yellow feed undercounts the event-unified target and is therefore not
the modelling target. The CSV keeps both feeds for auditability.

## 4. Defects and modelling consequences

- 2024/2025 is score-only and cannot support stats, event-card, or HT-derived
  feature estimation.
- No shotmap, xG, or xGOT exists in any era; no such feature is invented.
- Referee is absent in both complete seasons and is present in only 93 / 94
  matches in the in-progress season.
- Two 2025/2026 matches are awarded; they are excluded from every fit and
  scored window.
- Stats yellow cards undercount event-unified yellows; event-unified yellows
  are the frozen cards target.
- Six-team season-boundary churn is a structural transition risk.
