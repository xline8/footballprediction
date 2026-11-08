# Step 1 — Data Understanding: GE-Erovnuli (Erovnuli Liga, FotMob id 439)

Resumed 2026-11-09 from `CHECKPOINT_HOLD_2026-11-09.md`; every sample
fact in the checkpoint was re-verified corpus-wide on resume (builder's
own audit over all 1,059 files, 0 unreadable).

## Inventory

- n = 1,059 played matches. Calendar-year seasons: 2021–2025 complete
  at n = 180 each; 2026 in progress, n = 159 (2026-02-28 → 2026-11-08).
- 10 teams per season, 36 rounds, 18 distinct team ids overall.
- Warehouse quirk (from checkpoint, re-verified): per-match JSONs live
  in the MAIN checkout `~/workspace/footballprediction/data_enrichment/
  fotmob_world/Georgia/Erovnuli Liga/<season>/<id>.json`; the builder
  reads the index + JSONs from there.

## Format / phase rule (frozen)

- Single quadruple round-robin: 10 teams × 36 rounds = 180 matches.
  All 10 teams play in every month of every season including the last
  rounds (checked Nov subsets 2023/2024/2025: 10/10 teams) — there is
  NO championship/relegation split phase. **Phase rule: every match is
  regular season; no phase filtering or phase feature.**
- Promotion/relegation happens between seasons only: movers into
  2022: 2, 2023: 2, 2024: 1, 2025: 1, 2026: 3. The feeder tier
  (Erovnuli Liga 2) is not in this corpus, so no cross-tier data
  exists (see FEATURES X2).

## Field coverage (corpus-wide audit, all 1,059 files)

| field | coverage |
|---|---|
| score (`header.teams[].score` / `scoreStr`) | 1,059/1,059 |
| stats feed (`content.stats`) | null in 1,059/1,059 — ABSENT |
| shotmap | present as object, `shots` empty in 1,059/1,059 — ABSENT |
| period splits | 0/1,059 (index flag) — ABSENT |
| referee (`matchFacts.infoBox.Referee.text`) | empty in 1,059/1,059 — ABSENT |
| lineup | non-null in only 20 files (all 2022) — unusable |
| events (`matchFacts.events.events`) | Goal 2,891 + Half 1,937 + Card 233 |

- Events verdict: goal events are COMPLETE and exact — goal-event
  count equals the score total in 1,059/1,059 matches. Goal event
  times therefore carry a real 1H/2H split (used only for the frozen
  halves constant, presentation).
- Card events are FRAGMENTS: only 205/1,059 matches carry any, 233
  events total (~1.1 per such match vs a real-world ~4/match) — a
  partial feed (likely red-card-adjacent only). Not a cards target.
  `header.status` red-card counts (205 matches with ≥1) likewise
  cannot reconstruct a cards total.
- **Conclusion: GOALS-ONLY league.** SOT, corners, cards, total shots
  have no target in any payload source — not buildable, documented in
  MODEL_DESIGN's feasibility matrix, not silently skipped.

## Split discipline

- Dev: seasons 2021–2024 (2021 = training seed; evaluation 2022–2024).
- Virgin: season 2025 (n = 180, last complete season), read ONCE.
- 2026 is IN PROGRESS — excluded from dev, virgin, training and gate
  setting entirely (TRANSITIONAL; a season-end confirmatory read is a
  future, separately-registered step).
