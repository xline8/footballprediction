# League verdict — AU-Championship (FotMob 8938) — **0 PASS / 0 FAIL / 5 NOT BUILDABLE**

## What it is

The Australian Championship is a real second-tier competition — but
FotMob id 8938 is not it. Id 8938 is a parent container holding ten
competitions: nine state NPL leagues (1,246 matches) plus the true
Championship (87 matches). The Championship itself launched in
October 2025: 16 clubs in 4 groups of 4, double round-robin (6
rounds, 12 matches/group), top 2 per group to a 7-match final stage
(4 QF + 2 SF + 1 final). 2025 is complete (55 matches,
2025-10-10..2025-12-06; champion South Melbourne, 2-0 vs Marconi
Stallions in the final). 2026 is transitional (32 group matches,
rounds 1–4 of 6, 2026-10-15..2026-11-08; rounds 5–6 and the final
stage not in the warehouse). There is no 2021–2024 history: the
"1,333 matches" the index suggests span sub-tournaments, not seasons
of one league.

## Verdict table

| Candidate | Dev | Virgin | Verdict |
|-----------|-----|--------|---------|
| G-AUCH goals | No window (one complete season) | **Not read** for evaluation (n=32, SE ~8.6pp) | **NOT BUILDABLE** |
| S-AUCH SOT | No target in any payload | **Not read** | **NOT BUILDABLE** |
| C-AUCH corners | No target in any payload | **Not read** | **NOT BUILDABLE** |
| K-AUCH cards | No target; no referee in any payload | **Not read** | **NOT BUILDABLE** |
| T-AUCH total shots | No target in any payload | **Not read** | **NOT BUILDABLE** |

No arm passed or failed a gate, because no gate could be run: the
season-blocked frame needs a training season plus an evaluation
season and this league has only the one; the virgin (2026, n=32) has
a calibration SE of ~8.6–8.7pp against a 1pp clean-PASS threshold,
and pooled n=87 still gives ~5.3pp. A verdict there would be decided
by one or two goals. Nothing was fitted, no engine was built, no
predictions were issued, no halves constants were frozen (X1–X9 all
dropped — see `analysis/FEATURES.md`).

## Levels (the only target that exists)

Championship goals: 2025 mean 3.22/match (n=55), 2026 transitional
2.91 (n=32), pooled 3.10 (n=87) — a high-scoring league, above J1
(2.68) and its A-League sibling. Over 2.5: 56.4% / 62.5% / 58.6%.
Home win 47.3% in 2025 but 31.2% in 2026 — a small-sample swing
(SE ≈ 8–9pp), not a finding.

## Payload-level data-quality notes

- Index `has_stats` / `has_shotmap` / `has_period_splits` are `False`
  for all 1,333 rows. The flags are right about the substance
  (stats null 1,333/1,333; shotmap shots empty 1,333/1,333) but for
  the wrong reason: the shotmap key is present in all 1,333 payloads
  as an empty skeleton (`{shots: [], Periods: {All: []}}`).
- State leagues: 603/1,246 matches (48.4%) are `finished = False`
  and recorded 0-0 — the `finished` flag separates them exactly
  (only 19 finished state matches are genuine 0-0s). 5 state
  matches are explicitly postponed/abandoned. The Championship's
  7 recorded 0-0s are all finished matches — genuine draws.
- Format change 2025 → 2026: drawn group matches go to a shootout
  in 2026 (8/8 draws, no ET) and did not in 2025 (0/12 group draws).
  The stored score stays the drawn score.
- 2025 QF APIA–Marconi 1-1 went to ET + penalties; its stored score
  may include ET goals — flagged, never repaired.
- Lineups exist in only 15/1,333 payloads (all 2025 Championship
  group rounds 1–2) and carry no stats.
- `coverageLevel` is `lower` in 1,333/1,333 payloads.

## Note on the pooled alternative and the sibling

A pooled 1,333-match model was considered and rejected on structure:
ten disjoint competitions with no cross-state play (block-diagonal
design) and state scores 48% unrecorded. State-league ratings as
Championship priors were also rejected: same-season concurrent form,
not a prior-season mover offset, and unvalidatable with no
in-competition dev/virgin window. The A-League sibling cannot supply
a mover prior either — its 13 senior clubs and the Championship's 20
clubs are disjoint (zero overlap).

## Revisit condition

Earliest gateable build: dev = 2025+2026 (once 2026 completes) with
virgin = 2027; a multi-season dev needs 2025–2027 with 2028 as
virgin. Any revisit needs a new preregistration; nothing is
scheduled. If FotMob coverage improves (stats blocks appearing),
S/C/K/T become re-assessable on the same revisit — verified from
payloads, never from the index flags.

## League complete

**GIT STATUS: NOTHING IS COMMITTED.** Git history in the repo is
damaged (coordinator freeze, 2026-11-10 ~15:42 WIB); no git command
was run after the freeze. All artifacts below exist only as files in
worktree `~/workspace/wt-au-championship`, branch
`build/au-championship` (created before the freeze). The coordinator
will rebuild history and commit/merge afterwards.
