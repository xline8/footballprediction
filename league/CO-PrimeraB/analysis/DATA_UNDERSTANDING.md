# Step 1 — Data Understanding: CO-PrimeraB (Colombia Primera B, FotMob id 9125)

Builder's own corpus-wide audit over all 1,773 indexed files
(0 unreadable), cross-checked through a second aggregation path.

## Inventory

- Index n = 1,773 (league_id 9125), calendar-year season labels
  2021–2026: 278 / 289 / 310 / 310 / 308 / 278.
- **Warehouse trap (caught in audit): 134 files in season 2021 are
  UNFINISHED 0-0 placeholders** (`header.status.finished` false, no
  scoreStr, no events) — almost all of the 2021 Apertura regular
  season (108 of 120) plus its two quadrangular groups (24) and 2
  Clausura matches. They are not played matches and their "0-0" is
  not a result. **Played corpus = finished files only: n = 1,639**
  (2021: 144, 2022: 289, 2023: 310, 2024: 310, 2025: 308, 2026: 278).
- 16 teams per complete season (by FotMob team_id; team *names* vary
  across seasons — accents/rebrands, e.g. Atletico FC / Atlético FC —
  identity is team_id everywhere downstream).

## Format / phase rule (frozen)

Each calendar year holds TWO short tournaments (Apertura, Clausura).
Per tournament: a single round-robin regular phase (16 teams, 15–16
rounds), then a quadrangular semi-final phase (top 8, two groups of
4, 24 matches), then finals (tournament final; in some years also a
Championship Final between the two tournament winners and a
Promotion Playoff). Phase is carried in the payload by the
`infoBox.Tournament.leagueName` (2021–2025: "Primera B Apertura",
"… Playoff Grp. A/B", "… Final Stage", "… Grand Final", "Championship
Final") and by `general.matchRound` strings in 2026
("Clausura - Quadrangular - Round 3" etc.). Phase counts (finished):

| season | regular | quadrangular | final |
|---|---|---|---|
| 2021 (partial) | 115 | 24 | 5 |
| 2022 | 233 | 50 | 6 |
| 2023 | 256 | 48 | 6 |
| 2024 | 256 | 48 | 6 |
| 2025 | 256 | 48 | 4 |
| 2026 (in progress) | 240 | 36 | 2 |

**Phase rule (frozen): every finished match is modelled — regular,
quadrangular and finals alike — with the phase recorded per match in
the CSV (`phase` column). No phase filtering, no phase feature.**
The post-season phases are ~17% of each year, involve the same clubs
in the same tournament, and season-blocked fitting treats train and
target identically.

## Field coverage (finished corpus, 1,639 files)

| field | coverage |
|---|---|
| score (`header.teams[].score`) | 1,639/1,639 |
| stats feed (`content.stats`) | null in 1,773/1,773 indexed — ABSENT |
| shotmap | `shots` empty in 1,773/1,773 — ABSENT |
| period splits | 0/1,773 (index flag) — ABSENT |
| referee (`matchFacts.infoBox.Referee.text`) | 0 in 2021–2024; 141/308 in 2025; 236/278 in 2026 — absent in the whole dev era |
| events (`matchFacts.events.events`) | none in 2021; present 2022+ |

- Events verdict 2022+: goal events are NEARLY exact — goal-event
  count equals the score total in 288/289 (2022), 310/310 (2023),
  308/310 (2024), 307/308 (2025), 278/278 (2026) finished matches.
  Goal-event times therefore carry a real 1H/2H split on the
  event-exact subset (used only for the frozen halves constant,
  presentation). 2021 finished matches carry NO events at all, so
  2021 contributes no halves information.
- Card events: FRAGMENTS in 2022–2025 (77–96 events per season,
  65–77 matches — ~1.2 per such match vs a real ~5). In 2026 the
  feed looks complete (1,502 events: 1,423 yellow, 44 red, 35
  yellow-red; 269/278 matches) — but 2026 is in progress and no
  earlier season has a cards target, so no cards model can be fitted
  or gated. `header.status` red-card counts likewise cannot
  reconstruct a cards total for 2022–2025.
- **Conclusion: GOALS-ONLY league.** SOT, corners, cards and total
  shots have no target in any payload source for the dev/virgin
  windows — not buildable, documented in MODEL_DESIGN's feasibility
  matrix, not silently skipped.

## Season status / split discipline

- 2021 is a PARTIAL seed season (Apertura regular season largely
  missing as placeholders; the finished 144 are Clausura-weighted).
  It is used as the initial training window only, never evaluated.
- Dev: seasons 2021–2024 (evaluation 2022, 2023, 2024).
- Virgin: season 2025 (n = 308, last COMPLETE calendar year — both
  tournaments finished, last match 2025-12-02), read ONCE.
- 2026 is IN PROGRESS (278 finished to 2026-11-07; the Clausura
  quadrangular is under way) — excluded from dev, virgin, training
  and gate setting entirely (TRANSITIONAL; a season-end confirmatory
  read is a future, separately-registered step).

## Movers (context for FEATURES X2)

Primera A (FotMob id 274) IS in the warehouse. Clubs move between
the tiers every year. New-to-B clubs per season (by team_id):
2022: 1 (Cucuta, not from A), 2023: 2 (both relegated from A),
2024: 2 (both from A), 2025: 2 (both from A), 2026: 1 from A.
Relegated-from-A clubs' first-B-season performance is measured in
EDA F4 — it is consistent enough to pre-register an X2 mover arm.
