# Step 1 — Data Understanding: FO-Logmanssteypid (FotMob 9523)

## What this competition is

The Faroe Islands Løgmanssteypið is **not a league**. It is the Faroese
Cup, and the warehouse holds exactly **one match per year: the Final**.
Every payload's `general` confirms it: `leagueRoundName: "final"`,
`matchRound: "final"`, `leagueName: "Cup"`, `coverageLevel: "lower"`,
`parentLeagueId: 9523` (no parent container — the cup is its own id).
One final per year, nothing else: no earlier rounds, no semi-finals,
no replays.

## Inventory (warehouse index, verified against payloads)

| Season | Date | Final | Score (90') | Decider |
|--------|------|-------|-------------|---------|
| 2021 | 2021-12-04 | NSI Runavik vs B36 Tórshavn | 1–1 | Pen 3–4, B36 win |
| 2022 | 2022-10-29 | Klaksvik vs Vikingur | 0–1 | Full-Time, Vikingur win |
| 2023 | 2023-11-04 | B68 Toftir vs HB Tórshavn | 0–0 | Pen 3–5, HB win |
| 2024 | 2024-11-02 | B36 Tórshavn vs HB Tórshavn | 2–2 | Pen 3–4, HB win |
| 2025 | 2025-10-31 | Klaksvik vs Vikingur | 2–0 | Full-Time, Klaksvik win |
| 2026 | 2026-09-05 | Víkingur vs Klaksvik | 2–0 | Full-Time, Víkingur win |

**Total: 6 matches, 6 seasons, exactly 1 per season.** Index row count
(6) equals payload count (6); no missing or extra matches. All 6
finished, none cancelled/awarded. No season is in progress.

Correction to the brief's scouting: the index team names are **not**
NULL — `home`/`away` are populated on all 6 index rows and agree with
the payloads. (Spelling varies across years: "B36 Torshavn" 2021 vs
"B36 Tórshavn" 2024; "Vikingur" 2022/2025 vs "Víkingur" 2026 — the same
clubs, accent variants in FotMob's naming.)

## Field coverage per season (PAYLOAD-VERIFIED, not index flags)

Scores exist in 6/6 (from `header.teams[].score`; the events feed is
empty in all 6, so there is no second count to cross-check against).

| Field | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 | Total |
|-------|------|------|------|------|------|------|-------|
| Score | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | **6/6** |
| `content.stats` | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | **0/6** |
| Shotmap with shots > 0 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | **0/6** |
| Events feed (`matchFacts.events`) | 0 | 0 | 0 | 0 | 0 | 0 | **0 events** |
| Referee field | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | **0/6** |
| Lineup | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | **0/6** |
| Player stats | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | **0/6** |

This competition is **scores-only in the strongest sense**: not even a
goal-minute event feed exists, so no half split of any kind can be
derived. The index flags (`has_stats: False`, `has_shotmap: False` on
all 6 rows) agree with the payloads here — unlike the CO-Superliga
case, where the flags lied in the other direction. `content.shotmap`
is present as a key (`{"shots": [], "Periods": {"All": []}}`) but holds
zero shots in all 6 payloads.

## Format rules (frozen, from payloads)

- Single-match Final, one per calendar year, played Sep–Dec (2021 is
  the latest: 4 December; 2026 the earliest: 5 September).
- Draw at 90 minutes → **straight to penalties**: 3 of the 6 finals
  (2021 Pen 3–4, 2023 Pen 3–5, 2024 Pen 3–4).
  `firstExtraHalfStarted` / `secondExtraHalfStarted` are empty in all
  6 payloads, so there is **no extra time**.
- The 90-minute score is the modelled outcome for any goals market;
  the penalty shootout decides the trophy, not the match score, and is
  recorded only as context (no model is built).

## Teams

6 distinct clubs in 6 years (accent-normalised). Appearances
(matches): Klaksvik 3, Víkingur 3, B36 Tórshavn 2, HB Tórshavn 2,
NSI Runavik 1, B68 Toftir 1. No club plays more than 1 match in any
season — by construction, a final has two teams and each plays once.
The most frequent clubs hold 3 matches in 6 years, and two of those
are the same fixture repeated (Klaksvik vs Víkingur, 2022/2025/2026).
**No team has any within-competition history to learn from**: every
final's two teams arrive with zero prior Løgmanssteypið matches that
season, and at most 2 stale finals from earlier years.

## Scope check: are other cup rounds hiding under another id?

No. The warehouse holds exactly two Faroese competitions:
Løgmanssteypið (9523, 6 rows) and the Faroese Premier League (250,
135 matches per season × 6 seasons = 810 rows). There is no other
Faroese cup id, no "Cup" sibling, and no round other than "final"
anywhere under id 9523. The Premier League is a separate league, not
cup rounds — borrowing its ratings would be a Premier League model
wearing a cup label, and it cannot be validated in-competition (see
MODEL_DESIGN.md). Scope is **not** widened.

## The feasibility question (answered here, before any fitting)

A season-blocked walk-forward dev needs seasons with enough matches
for a team rating to exist and for LL / calibration to be estimated.
Here a "season" is 1 match between 2 teams that never meet again in
the competition that year. The three-legged gate cannot be evaluated:
the virgin window (2026) is n=1, where the calibration SE at OU 2.5
is ≈37pp (base rate 1/6) and ≈50pp at p=0.5 — 37–50× the 1pp
clean-PASS threshold — so a PASS/FAIL would be decided by a single
goal in a single match. Pooling all 6 matches does not save it either
(OU 2.5 SE ≈ 15.2pp at n=6). See `prereg/PREREG_FO_LOGMANSSTEYPID.md`
for the arithmetic. **Verdict: not buildable — all five candidates.**
No model is fitted, no virgin is read, no engine is built.
