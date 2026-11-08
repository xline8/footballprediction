# Step 2 — Preprocessing: PE-Liga1

Builder: `league/PE-Liga1/data/build_data.py` (regenerates
`pe_liga1_matches.csv` + `pe_liga1_team_matches.csv`, both gitignored;
counts asserted as floors so the daily runner can rebuild after
incremental additions). One row per played match, 1,860 rows.

## Inclusion rules (frozen)

1. **All 1,860 finished files enter the CSV.** Nothing is dropped at
   build time; every exclusion lives in the modelling layer via
   flags, so the audit trail is complete.
2. `phase`: `playoff` iff the payload sub-league name contains
   Final Stage / Championship Playoff / Qualification / Placement
   Playoff (15 matches); else `regular`.
3. `awarded`: from `header.status.awarded` (9 matches).
4. **Modelling corpus = `phase == regular` AND `awarded == 0`**:
   1,836 matches. Play-offs are excluded from all fitting and
   evaluation (knockout incentives, two-leg ties, and a 15-match
   tail cannot carry a gate); awarded matches were not played.
   - Dev (2021–2024): 1,216. Virgin (2025): 323. Reserved (2026,
     in progress): 297 — never read by any harness in this build.
5. `block` = (season, tournament): `2021 - Fase 1`, `2021 - Fase 2`,
   then `<year> - Apertura` / `<year> - Clausura`; 2026 blocks are
   split by the round-string prefix. All walk-forward fits are
   block-blocked: one fit per target block from matches strictly
   before the block's first match date.

## Column rules

- Score: `header.teams[].score`. HT goals: the Half event's HT score
  where present (1,821 matches), else goal-event times ≤ 45 under
  the `events_exact` guard, else missing (7 matches, all 2023).
- Stats: `content.stats.Periods` All + FirstHalf, first occurrence
  per key (duplicated sections are value-identical). Sparse-era
  matches simply lack the rich keys (NaN, never fabricated).
- Cards, three captures: stats-feed `yellow_cards_*` (rich matches
  only), event yellows plain (`ev_yellow_*`, Yellow only) and
  event yellows including second yellows (`ev_yellow_inc2nd_*`).
  First-half event yellows (`fh_ev_yellow_inc2nd_*`) for the halves
  constant. Which capture is the target is an EDA decision
  (EDA F-feed-1), frozen in the prereg before fitting.
- Unified total shots are **not** a CSV column; the target is
  derived in the engines from the documented rule (rich:
  `shotsontarget + shotsofftarget`; sparse: `total_shots`) so the
  raw captures stay auditable.
- Referee: `infoBox.Referee.text`, empty string when absent.
- Entrant flags: `home/away_absent_prev` = team id absent from
  Liga 1 in the previous calendar year (2021 rows: 0 by definition).
  There is no `mover_up` flag — no feeder league exists in the
  warehouse to confirm the source competition.
- Team names canonicalised per id (most frequent spelling).
