# Step 1 — Data Understanding — CL-LigaDeAscenso (Chile, FotMob id 9126)

Source: FotMob world warehouse, index filter `league_id = 9126`
(`data_enrichment/fotmob_world_index.csv`), per-match JSONs under
`data_enrichment/fotmob_world/Chile/Liga de Ascenso/<season>/<id>.json`.
All coverage numbers below were computed **from payload content**, not
from the index flags — in this league the flags lie (see below).

## Inventory (all rows; modelling population = finished + regular)

| season | rows | finished | fin. regular | fin. play-off | unfinished | dates |
|---|---|---|---|---|---|---|
| 2021 | 246 | 184 | 178 | 6 | **62** | 2021-04-03 – 2021-12-10 |
| 2022 | 280 | 280 | 272 | 8 | 0 | 2022-02-15 – 2022-11-27 |
| 2023 | 252 | 252 | 240 | 12 | 0 | 2023-02-10 – 2023-12-10 |
| 2024 | 252 | 252 | 240 | 12 | 0 | 2024-02-24 – 2024-12-07 |
| 2025 | 252 | 252 | 240 | 12 | 0 | 2025-02-21 – 2025-12-07 |
| 2026 | 233 | 233 | 233 | 0 | 0 | 2026-02-20 – 2026-10-31 |

Total 1,515 rows; 1,453 finished; modelling population 1,403
(finished, regular phase).

## Format (verified from the feed, not assumed)

Unlike the parent Primera — whose feed contains **no** play-offs at
all — the Ascenso feed **does** differ: every season has a regular
double round-robin **plus a promotion play-off (liguilla)**:

- Regular: 16 teams × 30 rounds = 240 matches (2021, 2023–2026);
  2022 had 17 teams × 34 rounds = 272. Calendar-year seasons.
- Play-offs: separate per-season instance ids named
  "Primera B Promotion Playoff" in 2021–2024 (rounds 1/4, 1/2,
  final; 6 / 8 / 12 / 12 ties), and in 2025 the same parent instance
  with round names "Promotion Play-offs - 1st Round / 2nd Round /
  Final" (12 ties). 2021 regular rows are split across two instance
  ids (9126: 230, 872610: 10, rounds 1–2 and one round-7 match) —
  both are the same regular competition.
- **Phase rule (frozen): play-off ties are EXCLUDED from every fit
  and every score.** Only `phase = regular` rows enter any window.

2026 is **incomplete** (233 of 240 regular matches played, round 30
only 1 match in, play-offs not started): reserved confirmatory
window, never read in this build. The last complete season, and
therefore the virgin, is **2025**. Dev = scored 2022–2024 with 2021
as warm-up/seed.

## DEFECT — fake 0-0 placeholders in 2021

62 rows in 2021 (concentrated Apr–Jun) have
`header.status.started = False, finished = False` and carry a
placeholder score of 0-0. They are fixtures FotMob never marked as
played; treating them as results would poison any fit (the raw 2021
regular "level" reads 1.775 goals/match with a 52.1% draw rate; on
finished rows only it is a sane 2.393 goals/match, 37.1% home wins).
Inclusion rule: **played ⇔ `finished = 1`** (PREPROCESSING). All
other seasons are 100% finished, so the defect touches only the
2021 warm-up season — dev and virgin are unaffected. Five ordered
home/away pair duplicates in 2021 all involve these placeholders
versus their rescheduled played versions.

## The stats era does not exist (index flags are false positives)

The index flags `has_stats = True` on 483 rows (250 in 2025, 233 in
2026). Verified from payload content, this is a **key-presence
artefact, exactly the TH-ThaiLeague2 failure mode**:
`content.stats` is `None` in every 2021–2024 payload, and in all
483 flagged payloads it is a shell `{"Periods": {"All": null}}`.
**Zero matches in any season carry a single stat value** — no SOT,
no corners, no total shots, no possession, no box touches, and no
period splits (`FirstHalf`/`SecondHalf` never appear). The shotmap
is an empty list in every payload and `expected_goals` appears
nowhere: there is no xG of any kind. Consequences are recorded in
MODEL_DESIGN: SOT / corners / total shots are NOT BUILDABLE (no
target exists in any window, virgin included).

## Events feed eras (matters for cards and for goal halves)

- **2021: the event feed is completely empty** (0 events in all 246
  payloads).
- **2022–2024: partial feed.** Events exist on 730/766 rows and goal
  events reconcile exactly with the score in 747/752 finished
  regular matches (5 truncated matches: 1 in 2023, 4 in 2024, each
  missing all its goal events). Card events in this era contain
  **only Red and YellowRed — zero plain Yellow events in three full
  seasons** (2022: 0 Yellow / 51 YellowRed; 2023: 0 / 50; 2024:
  0 / 38).
- **2025–2026: full feed.** Every match has events; plain Yellow
  events appear (1,514 in 2025; 1,111 in 2026 so far).

**Cards artefact check (run before any fitting, per program rule):**
the stats-vs-events comparison the rule envisages **cannot be run —
there is no stats source at all** (stats yellow rows: 0 in every
season). The substitute check is the event feed itself, and it fails
in the opposite direction to the parent league: here the *event*
feed omits plain yellows entirely before 2025. An event-unified
yellow target therefore exists only in 2025 (virgin candidate) and
2026 (incomplete) — **no scorable dev window contains the target,
so cards are NOT BUILDABLE** (MODEL_DESIGN). No target is frozen
because no candidate is built; if a future warehouse refresh adds
pre-2025 stats or plain-yellow events, the artefact check must be
re-run and the target frozen then.

## Other fields

- Referee (`infoBox.Referee.text`): present on 56/1,515 matches —
  0 in 2021–2024, 54 in 2025, 2 in 2026. No referee covariate is
  possible.
- Team identity: 25 distinct FotMob ids; ids are **stable**, names
  are not. Four ids carry multiple spellings (192436 Deportes
  Copiapo/Copiapó; 4061 Union/Unión San Felipe; 4054 Universidad de
  Concepcion/Concepción; 162905 Curico Unido/Curicó Unido). The
  builder keys everything on team id and canonicalises the display
  name to the last-seen spelling.
- Tier movers (for X2): the parent tier CL-LigaDePrimera (id 273)
  corpus exists. Exactly **2 relegated teams** join the Ascenso
  each season (2022: Melipilla, Santiago Wanderers; 2023:
  Antofagasta, La Serena; 2024: Curicó Unido, Magallanes; 2025:
  Deportes Copiapó, Cobreloa; 2026: Deportes Iquique, Unión
  Española), plus 1 arrival per season from the third tier (no
  corpus: Recoleta, San Marcos, Limache, Concepción, Puerto Montt).
