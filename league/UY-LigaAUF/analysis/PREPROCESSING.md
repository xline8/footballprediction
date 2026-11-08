# Step 2 — Preprocessing: UY-LigaAUF

Builder: `data/build_data.py` (adapted from the QA-QatarStars
builder; derivation rules unchanged unless UY-forced and noted
below). Inputs: bundle index `index_161.csv` + extracted release
`data_enrichment/fotmob_world/Uruguay/Liga AUF Uruguaya/<year>/*.json`.
Outputs: `data/uy_matches.csv` (1,717 rows) + `data/uy_team_matches.csv`
(3,434 rows).

## Derivation rules (PLAYBOOK, unchanged)

- FT score from `header.status.scoreStr` (authoritative; see the two
  mismatch cases below).
- Team stats from `content.stats.Periods` — absent in all 1,717
  payloads, so every stats column is None with `has_stats_all` /
  `has_stats_half` False. Missing stays missing; no absent feed is
  read as zero.
- 1H goals / 1H cards counted from event times (minute ≤ 45,
  incl. 45+ stoppage notation) — only for matches with an events
  payload; the 38 payload-less matches get HT None (`ht_source`
  "none").
- Phase from `general.leagueName`: contains "Intermedio" →
  `intermedio` (incl. Grp. A/B and Intermedio Final Stage);
  "Apertura" → `apertura`; "Clausura" → `clausura`; "Final Stage"
  (without Intermedio) → `final_stage`. All phases are ordinary
  rows.
- Keyed by FotMob team id; each id carries one canonical name
  (see below).
- Cards: BOTH sources recorded — stats-feed yellows (all None:
  feed absent) and event-derived counts (`ev_yellow_*`,
  `ev_yellowred_*`, `ev_red_*`). The unified `yellow_*` /
  `red_*` target columns stay None with `cards_source` "none":
  there is no consistent yellows target (stats absent everywhere;
  event plain Yellows only from 2023 — a definition break inside
  dev). Event counts are None (not 0) for the 38 payload-less
  matches.

## UY-forced notes

- Season label is the calendar year ("2021" … "2026");
  `season_start` is that year.
- Team-name canonicalisation (accent variants of the same id):
  id 1838 "Club Atletico Progreso" (34) → "Club Atlético Progreso"
  (105); id 8450 "Club Atletico Penarol" (212) →
  "Club Atletico Peñarol" (11) — canonical is the majority spelling
  in each case (most-common wins: 8450 keeps "Club Atletico Penarol");
  id 1834 "Central Espanol" (24) → "Central Español" (11).
  Canonical name = most-common spelling per id, applied to both
  CSVs.
- Score-vs-events mismatches (2/1,679): 3834312 awarded 0–3
  (events 2–1); 4425121 scoreStr 5–0 vs 6 Goal events. scoreStr
  kept; `score_events_mismatch` flags both; both are excluded from
  the event-time halves share. No other match is affected.
- 1 awarded match in the corpus (3834312, 2022). It is an ordinary
  row for goals modelling (the awarded 0–3 stands as the result).
- Empty-events matches (38, all 0–0): `ev_goals_*` None,
  `ht_*` None, `ev_*` card counts None. Their scoreStr goals (0–0)
  are real and used.
- No imputation anywhere. No target is imputed; no absent feed is
  read as zero.

## Verification (PLAYBOOK self-check)

- CSV match count == index count: 1,717 == 1,717; team rows 3,434;
  26 team ids; 16 teams/season every season.
- 3 raw-JSON spot checks by hand: 3583874 (Montevideo City Torque
  0–1 Sud America), 3583875 (Montevideo Wanderers 1–0 Boston
  River), 3583877 (Villa Espanola 0–0 Progreso) — scores, phases
  (apertura), and finished flags all match the CSV.
- Every row `finished=True`; `home_goals`/`away_goals` non-null
  in all 1,717 rows.
