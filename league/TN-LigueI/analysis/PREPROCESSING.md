# Step 2 — Preprocessing: Tunisia Ligue I

Source CSV: `league/TN-LigueI/data/tn_matches.csv` (1,060 rows),
built by `league/TN-LigueI/data/build_data.py` from the FotMob
world warehouse (index league_id 544). The CSV is gitignored by repo
norm (`*.csv`); the builder script is the reproducible source. The
builder must be run with the main checkout as BASE (the warehouse
payloads are gitignored and do not exist inside a worktree):
`python3 build_data.py /home/hatch/workspace/footballprediction`.

## Inclusion rules

- **Played matches only.** Every index row is a played match
  (`finished=True`, header scores present in 1,060/1,060), so no rows
  are dropped for missing scores. Zero duplicate match_ids.
- **Model data = all phases except awarded matches**
  (`is_awarded == 0`, n = 1,051 = 156 + 195 + 170 + 237 + 237 + 56).
  Group, championship, relegation, placement and single-table
  regular matches ALL enter every fit, baseline, and metric: they
  are league matches with 90-minute scores (no extra time anywhere),
  and the harness must filter on `is_awarded == 0` only — never on
  phase. The 9 awarded matches (`is_awarded == 1`) are EXCLUDED from
  every fit, baseline, and metric (AE-ProLeague precedent): their
  header scores are forfeit scores, not football results. The CSV
  keeps them (flagged) for inventory completeness.
- **Season labels as in the warehouse:** "2021/2022" … "2026/2027"
  (index `season` column). No relabelling.
- **Team identity** is keyed by FotMob team id
  (`header.teams[].id`); names are carried for readability only.
  Team ids are stable across seasons; the same id appears under
  accent-variant spellings (8153 Esperance/Espérance, 102104
  Olympique de Beja/Béja, 405958 Etoile Metlaoui/Métlaoui), so any
  name-keyed join is a defect. Entrants are new ids (see EDA F4).

## Split-source rules (never fabricate)

- **Goals 1H/2H:** from goal-event times only (`content.matchFacts.
  events.events`, `type == "Goal"`, `time <= 45` is 1H; minute-45
  goals with `overloadTime` set are 1H stoppage time, still 1H).
  Cross-checked against the HT Half event (`type == "Half"`,
  `halfStrShort == "HT"`): agreement in all 925 matches where both
  exist (0 disagreements), so the two sources are interchangeable
  and the goal-time derivation is the primary one (LU/NI precedent).
- **Awarded matches (9):** halves EMPTY (missing, not zero) — their
  event trails disagree with their header scores. They contribute
  nothing to any FT or halves tally in model data (excluded).
- **0-0 matches with no events (133):** 1H goals = 0 by construction
  (contribute 0/0 to the share). No imputation is performed anywhere
  else. The builder asserts that no non-awarded match with goals
  lacks an event feed.
- **No other splits exist.** There are no 1H SOT/corner/card splits
  because those targets do not exist in any payload. No split is
  ever synthesised from a league average at match level; the frozen
  halves constant (EDA F3) is applied only at presentation time, on
  PASS, to FT lambdas.

## Windows

- Warm-up: 2021/2022 (n=156 model rows).
- Dev scored: 2022/2023–2024/2025 (n=602 model rows).
- Virgin: 2025/2026 (n=237 model rows, complete) — read ONCE, only
  for dev-passing arms.
- Confirmatory reserve: 2026/2027 partial (n=56 model rows, rounds
  1–7) — untouched by every step in this league.
