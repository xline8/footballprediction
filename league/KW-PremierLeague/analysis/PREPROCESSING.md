# KW-PremierLeague — Preprocessing (Step 2)

Build: `data/build_data.py` (adapted from the BY-PremierLeague
scores-only build) → `data/kw_matches.csv` (642 rows) +
`data/kw_team_matches.csv` (1,284 rows). Counts verified: 642 played
+ 69 unplayed = 711 index rows; 3 raw-JSON spot checks pass
(3518338 1–3; 4067510 awarded 0–3; 5800351 1–1).

## Canonicalisation decisions (frozen)

1. **Dual season labels 2021 / 2021/2022 — kept as two distinct
   seasons, no deduplication.** Evidence: 0 shared match ids,
   disjoint date ranges (Jan–May 2021 vs Nov 2021–Apr 2022),
   different team sets. The labels are used verbatim from the index;
   the canonical season order is
   2021 < 2021/2022 < 2022/2023 < 2023/2024 < 2024/2025 < 2025/2026 <
   2026/2027. (The raw-JSON folders use dashes, `2021-2022`; the
   index path column is remapped to the extracted tree.)
2. **Unplayed fixtures excluded.** 69 index rows with
   `finished=false`/`started=false` and placeholder index score
   "0-0" are not matches and never enter any CSV (26 / 21 / 12 / 10
   in the first four seasons; none later). This is the SE-Ettan
   precedent: placeholder 0-0 rows are not results.
3. **FT score from `header.status.scoreStr`** — never the index
   score, never event-derived (events agree with the header in all
   237 event matches anyway).
4. **Phases are ordinary rows** with a flag from
   `general.leagueName`: main / championship / relegation. Nothing
   is filtered by phase.
5. **The one awarded match** (4067510, 2022/2023) is an ordinary row
   with `awarded=true`; the header score is used.
6. **Missing stays missing.** The stats feed is absent in all 711
   payloads, so every stats column is empty (NaN) with
   `has_stats_all = has_stats_half = 0` throughout — an absent feed
   is never read as zero. The same for shotmap aggregates (0 shots
   recorded as feed-absent: `has_shotmap = 0` everywhere) and for
   1H fields in the 405 matches without events (`ht_source = "none"`,
   ht goals NaN — note 374 of those matches DO have goals, 1,219 in
   total; their halves are unknown, not zero).
7. **Cards recorded from both sources per the playbook:** stats
   yellows (absent everywhere → NaN) and event-derived yellows
   (Yellow + YellowRed count one each). The event feed carries only
   Red cards in this corpus (53 total; 0 Yellow, 0 YellowRed in any
   season), so event yellows are a true observed 0 in event matches
   and missing elsewhere — but with no era in which a yellows target
   exists at all, this never becomes a modelling target (EDA F5).
8. **Keys are FotMob team ids** (14 ids, one name each — verified;
   no canonicalisation of names needed).

## Derivation rules applied

- 1H goals counted from goal-event times (minute ≤ 45 incl. stoppage)
  where events exist — in dev that is only 2024/2025 (87 matches).
- Team table: one row per team per match with goals for/against and
  the (all-empty) stats mirrors, keyed by team id.
