# Step 1 — Data Understanding (CZ-Liga, Czechia 1. Liga, FotMob id 122)

Corpus: FotMob world warehouse, index `data_enrichment/fotmob_world_index.csv`
filtered to league_id 122. **1,492 played matches** in the index, seasons
2021/2022–2025/2026 complete plus 2026/2027 in progress (111 matches,
regular-phase rounds 1–14 only). Every number below was measured on the
payloads (coordinator inventory + builder extraction, cross-checked).

## League format — the Czech split (verified from the feed, not assumed)

16 clubs. Each complete season in the warehouse = **276 matches (277 in
2023/2024)**, in FOUR sub-tournaments distinguished by `general.leagueName`
(and distinct sub-league ids):

| Sub-tournament | n/season | Structure |
|---|---|---|
| `1. Liga` (regular) | 240 | 30 rounds × 8, double round-robin |
| `1. Liga Championship Group` | 15 | places 1–6, single round-robin, points carried over |
| `1. Liga Relegation Group` | 15 | places 11–16, single round-robin, points carried over |
| `1. Liga Placement Matches` | 6 (7 in 2023/2024) | places 7–10 knockout for the European slot: two-legged semi-finals (round label `1/2`) + two-legged final; in 2023/2024 one extra one-off `final` (2024-05-31, Mlada Boleslav–Hradec Kralove, the placement winner vs the cup-slot holder) makes 7 |

Note the trap: split-group rounds reuse round numbers 1–5, so `matchRound`
alone cannot separate phases; `leagueName`/sub-league id can, exactly.
**Phase rule (frozen in PREPROCESSING):** regular + championship +
relegation groups are modelled as ordinary matches (points-carrying league
phases, SCO/RO precedent); Placement Matches are EXCLUDED everywhere
(knockout, two-legged, different incentives — the RO `ecl_playoff`
analogue). Included n = **270 per complete season**, 1,461 total
(+111 in-progress). One extra-time nuance: 2 matches carry extra-time
period blocks — both are placement matches, hence excluded anyway.

## Field coverage (measured)

| Field | Coverage |
|---|---|
| FT score (header) | 1,492 / 1,492 |
| matchFacts events | 1,492 / 1,492 (13,351 subs, 6,389 cards, 4,147 goals, 80 missed pens) |
| Stats `Periods.All` | 1,480 / 1,492 (missing 4 in 2021/2022, 7 in 2023/2024, 1 in 2024/2025; of included matches: 3/7/1) |
| Stats keys, dev era (2021/22–2024/25) | ONLY `BallPossesion`, `total_shots`, `ShotsOnTarget`, `corners` |
| Stats keys, rich era (2025/2026+) | + blocked shots, off-target, touches_opp_box, big_chance, stats yellow/red cards, fouls, etc. — 388 matches only |
| Period splits (FirstHalf/SecondHalf) | ONLY 2025/2026+ (387 matches) — **no dev-era halves source for stats markets** |
| Shotmap | empty in ALL 1,492 matches |
| xG (`expected_goals` any period) | **absent in ALL matches** → goals model is goals-only |
| Referee | `infoBox.Referee` dict present in 1,492/1,492 BUT `text` is **empty in every dev-era match** (0/1,105); names exist only 2025/2026 (241/276) and 2026/2027 (109/111) |

## Feed defects found (stated plainly)

1. **Total-shots counting break at 2025/2026**: dev-era mean 16.4–18.3 per
   match → 25.65 in 2025/2026, 28.09 in 2026/2027 (+44%), while goals,
   SOT and corners are continuous across the boundary. The dev-era
   `total_shots` counts a narrower quantity (components to verify it —
   blocked/off-target — are not stored in the dev era). Same disease as
   RO-LigaI. Consequence: T-CZ not buildable (Step 6).
2. **Referee names absent in the dev era** (defect 1's sibling): the field
   exists but is blank until 2025/2026. X8 referee feature cannot be
   reliability-tested or armed in dev → dropped (FEATURES).
3. **Goal events ≠ score in exactly 1 match**: 2026-05-09 Slavia Prague–
   Sparta Prague (championship group, virgin season), score 0–3 but 5
   Goal events — two disallowed home goals (32', 52') are retained as
   Goal events. Header score is authoritative for all targets; event
   goals are used ONLY for the halves constants (measured on the dev
   era, which is clean: 4,142 events vs 4,142 score goals there — the
   corpus-wide 4,147 vs 4,145 gap is entirely this match plus its
   second disallowed goal). The match's event-derived HT counts
   overstate home 1H goals by 1 — presentation-only impact.
4. **Cards stats-vs-events artefact (mild, measured)**: where both exist
   (388 rich-era matches), stats `yellow_cards` vs event yellows agree
   exactly in 332/388 (85.6%); diffs are mostly ±1 including a few
   home/away attribution swaps; means 3.78 (stats) vs 3.88 (events);
   reds agree 386/388. The event feed is complete in EVERY era at
   plausible levels (3.75–4.58 yellows/match) — this is **not** the
   TH-style era flip (TH had no plain-yellow events in its dev-era
   feed). Target frozen as event-unified yellows (PREPROCESSING).

## Team identity

Keyed by FotMob team id — stable across all seasons. **19 distinct club
ids** under 26 name strings: diacritic variants appear in 2026/2027
(Baník/Banik Ostrava id 6362, Viktoria Plzeň/Plzen 6033, Hradec
Králové/Kralove 1712, Slovácko/Slovacko 2021, Mladá/Mlada Boleslav
10180) and one sponsor rename (FC Fastav Zlin 2021/2022 → FC Zlin →
FC Zlín, id 1860). Canonical name = most recent string per id
(`data/cz_teams.csv`). One club is promoted/relegated per season in
this window (Zbrojovka Brno up 2022, Karvina 2023, Dukla Praha 2024,
FC Zlin 2025; the 2nd tier FNL, id 253, is in the warehouse with
240 regular-season matches/season → mover analysis feasible).
