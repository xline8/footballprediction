# Step 2 — Preprocessing: SE-Ettan

Builder: `data/build_data.py` (adapted from the QA-QatarStars builder;
derivation rules unchanged unless SE-forced and noted). Outputs
`data/se_matches.csv` (2,662 rows) and `data/se_team_matches.csv`
(5,324 rows), sorted by (date, match_id). Season label is the calendar
year (`"2021"` … `"2026"`); `season_start` is that year and defines
all windows. All windows in this build are season-based: dev ≤ 2024,
virgin = 2025, 2026 untouched.

**Deliberate deviation from the "CSV count == index count" check
(documented in the builder and in Phase 1): the index lists 2,880
rows, but only 2,662 matches were actually played.** The other 218
are 2021 fixtures that were never started (`finished` false, no
`scoreStr`; the index carries a placeholder `"0-0"` for all 218).
Ground truth is the raw JSON: unplayed fixtures are EXCLUDED from
the CSVs, never counted as 0–0. The replacement check holds exactly:
CSV count == played count verified in raw JSONs, per season
(2021: 262, 2022–2025: 480 each — `eda.py` re-verifies this:
`csv_vs_raw_played_match` is true for all five seasons).

Rules, as in the reference:
- Missing stays missing (NaN) with provenance flags; targets are never
  imputed; absent feeds are never read as zeros.
- Scores come from the header `scoreStr` (authoritative; event-goal
  counts are a cross-check — exactly 1 mismatch in 2021–2025:
  4398485, see below). The mismatched match is excluded from the
  halves-goals share; it is an ordinary row everywhere else.
- HT goals and HT cards from event times, first half = event time ≤ 45
  (FotMob files 45+2' under time 45). A match WITH an events payload and
  no goal/card events gets HT 0–0; a match with no events payload gets
  HT missing (`ht_source = none`) — that is all 262 played matches in
  2021, so 2021 contributes no HT information at all.
- **Awarded match (SE-specific, measured)**: 4398485 (2024, Norra, AFC
  Eskilstuna 0–3 Umeå, `awarded=True`). Official score 0–3 is kept;
  the event feed shows 3–1 (goals at 16' away, 19'/63'/85' home), so
  its event-derived HT (1–1) does **not** reconcile with the official
  result and the match is excluded from the halves share. Its
  event-derived yellow counts (2 home / 1 away) are kept as evidence
  columns only.
- **Cards target (SE-forced)**: the unified target stays missing
  (`yellow_home` / `yellow_away` = None, `cards_source = none`) in
  every row — there is no stats feed anywhere in SE, so no stats
  yellows exist to unify. Event card counts are kept in `ev_*`
  columns as evidence (Yellow / YellowRed / Red, home and away, plus
  1H yellows `ev_yellow_1h` and `ht_yellow_*`). Unlike QA, the dev
  event feed DOES carry plain Yellow events (4,745 in dev), so the
  event-derived yellows are a real, measurable series 2022–2024 —
  but they are not adopted as the modelling target (see EDA.md F5:
  no stats feed to validate them against, and no events at all in
  2021, so no complete dev window from one consistent source).
- **Phase**: `norra` / `sodra` from `general.leagueName` (Ettan Norra /
  Ettan Södra). Both are ordinary regular-season rows, never dropped.
  No playoffs exist in this feed.
- **Referee** from `content.matchFacts.infoBox.Referee.text`, empty
  string stored as missing; `has_referee` flags named referees (0 in
  every season).
- **Team names**: 5 ids carry two spellings each (see
  DATA_UNDERSTANDING.md); the builder canonicalises to the
  most-common spelling. All logic is keyed by FotMob team id.
- Stats halves: none — there are no FirstHalf/SecondHalf period
  splits in any season (`has_stats_half` false everywhere).
- Shotmap aggregates: none — the feed has no shotmap in any match
  (`has_shotmap` false for 2,662/2,662).
- 2026 rows are built into the CSVs (program precedent: CH/QA reserve
  seasons are built but never used in any analysis, fit, or gate).
  No analysis in this league reads 2026.

## Spot checks (verified by hand against raw JSON in this phase)

1. **3518458, 2021** (Brommapojkarna 2–0 IF Karlstad, round 1, Södra):
   no stats, no events, no referee, no shotmap, no 11-starter lineup;
   score from header 2–0; HT goals missing (`ht_source = none`). ✓
2. **4086707, 2023** (Vänersborgs IF 0–3 IK Oddevold): goal events at
   26' and 32' (away) and 56' (away) → HT 0–2; score from header 0–3;
   event yellows 1 home / 0 away. ✓
3. **4398485, 2024** (AFC Eskilstuna 0–3 Umeå, awarded): header 0–3
   kept; event goals 3–1 (16' away, 19'/63'/85' home) → mismatch flag
   true, excluded from halves share; event yellows 2–1 kept as
   evidence only. ✓
4. **3518411 / 3518412, 2021** (unplayed fixtures, Södra round 2):
   `finished` false, `scoreStr` null in raw JSON; index carries
   `"0-0"`; neither row is in the CSVs. ✓
