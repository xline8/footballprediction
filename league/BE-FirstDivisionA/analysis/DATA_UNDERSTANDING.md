# Phase 1 — Data Understanding: FotMob Belgium First Division A Warehouse

Corpus: `data_enrichment/fotmob_world/Belgium/First Division A/` —
1,698 full matchDetails JSONs (league_id 40), seasons 2021/2022 →
2026/2027. Every number below was measured on the files via the index
(`fotmob_world_index.csv`, league_id = 40) and the built CSV
(`analysis/eda_compute.py` → `eda_numbers.json`).

## 0. Integrity headline

- 1,698 index rows = 1,698 files = 1,698 built match rows; match ids
  unique; every match finished. Index depth flags: stats 99.9%,
  shotmap 99.9% — confirmed by content (see §2).

## 1. League format — three eras, play-offs in every complete season

Belgium's format is the most complex in the program so far. It
changed shape twice inside the corpus, and **every complete season
ends in play-off groups whose points are halved** — the phase of
every match is flagged in the CSV from the JSON's own
`general.leagueName` (the tournament name FotMob itself assigns),
never inferred from round numbers (FotMob's `matchRound` numbering
for the play-offs is inconsistent: it restarts at 1 in 2021/2022 and
2024/2025+, but continues 31–40 in 2023/2024).

| Era | Seasons | Teams | Regular | Play-offs | Matches/season |
|---|---|---|---|---|---|
| Old play-offs | 2021/2022, 2022/2023 | 18 | 34 rounds, double RR (306) | Play-offs 1 (top 4, double RR, 12) + Play-offs 2 / ECL group (teams 5–8, double RR, 12); points halved on entry | 330 |
| New play-offs | 2023/2024 → 2025/2026 | 16 | 30 rounds, double RR (240) | Champions' group (top 6, double RR, 30) + Europe/ECL group (7–12, double RR, 30) + Relegation group (bottom 4, double RR, 12) + 1 ECL final; regular points halved on entry to the champions'/relegation groups | 313 |
| Classic (return) | 2026/2027 (partial) | 18 | double RR, **no play-offs** | — | 99 played (11 rounds) |

- Measured phase counts match the format table **exactly** in every
  season (306+12+12; 240+30+30+12+1) — the flag is verified, not
  assumed. Phase values: `regular`, `playoff_championship`,
  `playoff_europe`, `playoff_relegation`, `playoff_final`.
- **Phase decision (frozen in MODEL_DESIGN + every prereg): all
  phases are INCLUDED in the same rating windows.** Reasoning:
  (1) the point halving is standings arithmetic — it does not touch
  the per-match generative process (goals, SOT, corners, cards,
  shots in 90 minutes) that every candidate models; (2) play-off
  matches are official league matches between the same squads,
  played within weeks of the regular season — excluding them would
  blind every rating window for the last 5–6 weeks of each season
  and discard 24/330 (7%) to 73/313 (23%) of each season in a league
  that is already thin; (3) repeated fixtures between the same teams
  are already the norm (double/triple round-robin); the play-off
  double round-robins add no new dependence structure; (4) measured
  phase levels (complete seasons) differ modestly from regular-season
  levels versus season-to-season swings — championship group:
  goals 2.75, corners 8.87 (the one notable dip, n=114); Europe
  group: goals 3.04, yellows 3.08; relegation group (n=36): goals
  3.14 — recorded in EDA, and the flag stays available so any future
  exclusion is an explicit, countable choice. No phase feature is
  used as a model input anywhere.
- Team churn: 24 distinct team ids ever; 16–18 teams per season with
  promotion/relegation swaps most seasons. The feeder tier (First
  Division B) is not in this corpus, so no cross-tier offset is
  estimable (contrast J.League F4); thin-data newcomers are handled
  by the goals candidate's pre-registered SHRINK arm. Team identity
  is keyed on FotMob team id everywhere: several clubs appear under
  two display names under one id (Standard Liege / Standard Liège,
  RWD Molenbeek / RWDM Brussels, RAAL La Louviere / La Louvière).
- Calendar: autumn–spring (Jul–May) with a winter break. 2026/2027
  is partial (99 matches, rounds 1–11, through 2026-11-08) and is
  reserved as the confirmatory window; it is running hot (3.19
  goals/match, 28.6 shots) — a level fact, not a modelling input.

## 2. Coverage matrix (share of matches with real content)

| Season | n | Stats FT | Stats per half | Shotmap | xG (stats) | touches_opp_box | Referee (non-empty) |
|---|---|---|---|---|---|---|---|
| 2021/2022 | 330 | 100% | 3.3% | 99.7% | 99.7% | 71.2% | 41.2% |
| 2022/2023 | 330 | 100% | 20.3% | 100% | 100% | 69.7% | 97.0% |
| 2023/2024 | 313 | 99.7% | 99.4% | 99.7% | 99.4% | 80.8% | 99.4% |
| 2024/2025 | 313 | 100% | 100% | 100% | 100% | 100% | 100% |
| 2025/2026 | 313 | 100% | 100% | 100% | 100% | 100% | 93.0% |
| 2026/2027 (partial) | 99 | 100% | 100% | 100% | 100% | 100% | 100% |

- Per-half periods are essentially absent before 2023/2024 (3.3%,
  20.3%). Halves constants are measured on the complete era only
  (2023/2024–2025/2026), exactly as CH/DK treated their partial eras.
- Three matches lack the stats-feed cards/xG block (1 in 2021/2022,
  2 in 2023/2024). One of them (4206400) has a real event feed: its
  cards come from events (`cards_source='events'`, 1 row) and its
  goals blend falls back to goals-only. **The other two are
  score-only matches** — 3604331 (2021/2022, stats feed is a stub:
  50/50 possession, 0 shots in a 5–0 match) and 4449361 (2023/2024,
  stats feed null) — with empty event feeds and no shotmap: only
  the score is real. The builder nulls every stats-derived field
  for such rows (`cards_source='none'`, 2 rows); their count-market
  targets are **absent, never zero**, and the count-market loaders
  exclude them (dev scored n = 955 for S/C/K/T; goals keeps them
  via its goals-only fallback). Nothing is fabricated. This was
  caught by the corners harness crashing on the null-feed match —
  the stub-feed match would otherwise have poisoned trailing
  windows with fake zeros.
- `expectedGoalsOnTarget` (xGOT) population break, same shape as
  DK/CH: populated only for on-target shots through 2023/2024
  (~35–36% of shots), ~99.7% from 2024/2025. Any xGOT trait is
  era-guarded to 2024/2025 onward.
- Referee (`matchFacts.infoBox.Referee.text`): only 41.2% populated
  in 2021/2022 (verified on raw JSONs — the name is genuinely
  absent), then 93–100%. Overall coverage ≈ 86%.

## 3. Definition alignment (measured)

| Concept | Source | Check |
|---|---|---|
| FT score | `header.status.scoreStr` | source of truth |
| HT score | goal events `time ≤ 45` | events present in 99.9% of matches |
| SOT | stats feed `ShotsOnTarget` | correlates 0.996 with the shotmap aligned definition (on-target AND not blocked); stats feed is source of record |
| Total shots | stats feed `total_shots` | shotmap present 99.9%; stats feed is source of record |
| Cards | stats feed `yellow_cards`; event fallback for the 3 stats-less matches | **explicit feed check (§4)**; stats feed is the unified source |
| Team xG | stats feed `expected_goals` | goals/xG pooled ≈ 0.97; per season 0.92–1.08 — FotMob xG runs slightly HIGH for BE in the recent era (goals below xG), the opposite sign of CH; the blend input is usable in every season |

## 4. Cards feed check (run early, per the program's standing warning)

Two earlier leagues found stats-feed card undercounts, so the check
was run before any design decision, on all 1,695 matches carrying a
stats-feed cards block:

- Exact total-yellows agreement stats vs events: **86.4%** of
  matches (85.9% when second-yellow `YellowRed` events are added to
  the event count — the gap is not a second-yellow artefact).
- Direction: stats feed is **lower** than events in 11.5% of
  matches, higher in 2.1%; mean difference −0.10 yellows/match;
  max absolute difference 3.
- Verdict: this is the **same shape DK measured** (86.2% exact,
  stats feed kept as the unified source) and far from a broken feed:
  one consistent source, consistently applied, with the event counts
  kept as cross-check columns (`ev_yellow_*`) for every row. The
  unified target is the stats feed; the −0.10/match tendency is a
  recorded level fact that the per-league fit absorbs. The sources
  are never mixed within the target (mixing would trade a small
  level bias for an inconsistent definition).

## 5. What this corpus has

- Full stats feed (xG with open-play/set-play/non-penalty splits,
  SOT, corners, cards, big chances, box touches) in essentially
  every match from 2021/2022 — a full xG-era corpus, like DK/CH.
- Per-half team stats from 2023/2024.
- Event timelines for 99.9% of matches; shotmaps for 99.9%.
- The program's most complex format history (§1) — handled by
  phase flags + season-blocked walk-forward, with the play-off
  inclusion decision frozen before any fitting.
