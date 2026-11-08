# Step 2 — Preprocessing: NI-Premiership

Source CSV: `league/NI-Premiership/data/ni_matches.csv` (1,242 rows),
built by `league/NI-Premiership/data/build_data.py` from the FotMob
world warehouse (index league_id 129). The CSV is gitignored by repo
norm (`*.csv`); the builder script is the reproducible source.

## Inclusion rules

- **Played matches only.** Every index row is a played match
  (`finished=True`, header scores present in 1,242/1,242), so no rows
  are dropped for missing scores. Zero duplicate match_ids.
- **Model data = regular season only** (`phase == "regular"`,
  n = 1,227 = 5 x 228 + 87). Playoff matches (`phase == "playoff"`,
  n = 15, 3 per complete season) are EXCLUDED from every fit, every
  baseline, and every metric: they are a different competition
  (European-place knockout) and their scores can include extra-time
  goals (3873126 went to 120'). The CSV keeps them (flagged) for
  inventory completeness; the harness must filter on `is_playoff == 0`.
- **Season labels as in the warehouse:** "2021/2022" … "2026/2027"
  (index `season` column). No relabelling.
- **Team identity** is keyed by FotMob team id
  (`header.teams[].id`); names are carried for readability only.
  Team ids are stable across seasons (verified: the same 12 names
  recur; entrants are new ids/names, see EDA F4).

## Split-source rules (never fabricate)

- **Goals 1H/2H:** from goal-event times only (`content.matchFacts.
  events.events`, `type == "Goal"`, `time <= 45` is 1H; minute-45
  goals with `overloadTime` set are 1H stoppage time, still 1H).
  Cross-checked against the HT Half event (`type == "Half"`,
  `halfStrShort == "HT"`): agreement in all 1,162 matches where both
  exist (0 disagreements), so the two sources are interchangeable
  and the goal-time derivation is the primary one (LU precedent).
- **3907917:** halves EMPTY (missing, not zero) — its event trail
  disagrees with its header score. It contributes its header total
  (3 goals) to FT tallies and 0 goals to the 1H/2H split.
- **0-0 matches with no events (64 without Half events, 73 with an
  empty events list):** 1H goals = 0 by construction (contribute 0/0
  to the share). No imputation is performed anywhere else.
- **No other splits exist.** There are no 1H SOT/corner/card splits
  because those targets do not exist in any payload. No split is
  ever synthesised from a league average at match level; the frozen
  halves constant (EDA F3) is applied only at presentation time, on
  PASS, to FT lambdas.

## Windows

- Warm-up: 2021/2022 (n=228 regular).
- Dev scored: 2022/2023–2024/2025 (n=684 regular).
- Virgin: 2025/2026 (n=228 regular, complete) — read ONCE, only for
  dev-passing arms.
- Confirmatory reserve: 2026/2027 partial (n=87 regular, rounds
  1–15) — untouched by every step in this league.
