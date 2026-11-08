# Pre-registration — AU-Championship (FotMob 8938)

**Committed before any fitting. No fitting is done under this prereg.**

## Feasibility verdict (the preregistered question)

Is there enough data for a season-blocked walk-forward dev + a virgin
window at all? **No — for every candidate.** This prereg records the
NOT BUILDABLE verdict with its payload-level evidence, so that no
fitting, no virgin evaluation, and no post-hoc arm can follow from it.

## Evidence (payload-verified 2026-11-10, 1,333/1,333 payloads read)

- FotMob id 8938 is a parent container of ten competitions. Only 87
  rows are the true Australian Championship (2025: 55 complete;
  2026: 32, transitional, rounds 1–4 of 6). The other 1,246 rows are
  nine state NPL leagues whose scores are 48.4% unrecorded
  (`finished = False`, recorded 0-0).
- Championship scores exist in 87/87 payloads (270 goals, mean 3.10
  per match); `content.stats` is null in 87/87, `shotmap.shots` is
  empty in 87/87, events are empty in 87/87, the referee field is
  blank, and there are no period splits. The only target that exists
  is goals.
- 20 distinct clubs across the two seasons; 12/16 retained 2025 →
  2026. Per-team matches: 6–9 in 2025, 4 so far in 2026. Zero club
  overlap with AU-ALeague (13 senior clubs), so no X2 cross-tier
  prior exists.
- The competition launched in October 2025: there is no 2021–2024
  history for it anywhere.

## Gate arithmetic (why no window exists)

- Dev = season-blocked walk-forward. It needs at least one training
  season plus at least one evaluation season. This league has exactly
  one complete season (2025, n=55), which can only be the training
  window (the analogue of J1's 2021). There is no evaluation season,
  and no prior-season climatology (no season before 2025).
- Virgin = 2026, n=32 (transitional). Calibration SE at OU 2.5 ≈
  8.6pp (over-rate 0.625) and at home-win rate ≈ 8.7pp — ~9× the 1pp
  clean-PASS threshold, so the PROVISIONAL band (±1 SE) would pass
  almost any arm. One goal in the virgin swings the over-rate by
  3.1pp. A PASS/FAIL there would be decided by one or two goals.
- Pooled n=87 does not rescue it: OU 2.5 SE ≈ 5.3pp, still 5× the
  clean threshold. Per-team n=6–9 cannot identify Dixon-Coles
  ratings to gate standard (32 ratings on 55 matches).
- A round-blocked within-season dev is a program-frame change, not a
  league decision, and is not run under this prereg.

## Registered decisions

- Arms: **none** (no candidate reaches design).
- Primary lines: **none chosen**.
- Virgin window (2026): **NOT READ for evaluation** for any
  candidate — deliberately unread, because no arm passes (or can
  pass) a dev gate. 2026 was tallied at inventory level only (n,
  rounds, dates, season levels in EDA.md) to establish that it is
  transitional; no model was fitted or scored against it. 2026
  remains usable only under a future prereg's terms.
- Format rules (frozen for the record): 16 clubs, 4 groups of 4,
  double round-robin (6 rounds), top 2 per group to a 7-match final
  stage (4 QF + 2 SF + 1 final); champion South Melbourne (2-0 vs
  Marconi Stallions, 2025-12-06). Drawn group matches go to a
  shootout in 2026 (8/8, no ET) and did not in 2025 (0/12 group
  draws); the stored score stays the drawn score. The 2025 QF
  APIA–Marconi 1-1 went to ET + penalties; its stored score may
  include ET goals — flagged, never repaired.
- Halves constants: **none frozen** (zero period-split observations).
- Features X1–X9: **all DROPPED** (see `analysis/FEATURES.md`).
- What ships: **nothing** — no engine, no fitted params, no predictions.

## Verdict

**0 PASS / 0 FAIL / 5 NOT BUILDABLE.** G-AUCH, S-AUCH, C-AUCH,
K-AUCH, T-AUCH are all NOT BUILDABLE. The league is complete on
this verdict. Earliest gateable revisit: dev = 2025+2026 (once 2026
completes) with virgin = 2027; a multi-season dev needs 2025–2027
with 2028 as virgin. Any revisit needs a new preregistration;
nothing is scheduled.
