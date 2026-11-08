# Pre-registration — Uzbekistan Superliga (FotMob 540)

**Committed before any fitting. No fitting is done under this prereg.**

## Feasibility verdict (the preregistered question)

Is there enough data for a season-blocked walk-forward dev + a virgin
window at all? **No — for every candidate.** This prereg records the
NOT BUILDABLE verdict with its payload-level evidence, so that no
fitting, no virgin evaluation, and no post-hoc arm can follow from it.

## Evidence (payload-verified 2026-11-10, 215/215 payloads read)

- FotMob id 540 is the only Uzbekistan league in the warehouse
  (`data_enrichment/fotmob_world_index.csv`: 215 rows, all
  `league_id = 540`, country Uzbekistan, league "Superliga"). There is
  no other Uzbek league, so no sibling/mover prior (X2) exists.
- Exactly ONE season exists: **2026** (calendar-year label), 215
  matches, 2026-02-27..2026-11-08, **IN PROGRESS**. There are zero
  complete seasons.
- Format (from payloads): 16 teams, double round-robin = 30 rounds x 8
  matches = 240 matches. Rounds 1–27 played (215 matches); round 26
  has 7 (Bunyodkor Tashkent vs Neftchi Fargona missing/postponed);
  rounds 28–30 not yet played (~25 matches outstanding). The season
  has not finished.
- Scores exist in 215/215 payloads (565 goals, mean 2.628 per match);
  index score agrees with `header.teams` scores 215/215;
  `general.finished` is True in 215/215.
- `content.stats` is null in 215/215, `content.shotmap.shots` is empty
  in 215/215, `content.lineup` is null in 215/215, the referee field
  (`matchFacts.infoBox.Referee`) is blank in 215/215, and there are no
  structured period splits. The index flags (`has_stats`,
  `has_shotmap`, `has_period_splits` all False) are right about the
  substance here, but for the wrong reason in one case: the shotmap key
  is present in all 215 payloads as an empty skeleton
  (`{shots: [], Periods: {All: []}}`), and `content.stats` is present
  as null.
- `matchFacts.events` is non-empty in 99/215 payloads (rounds 10 and
  14–27 — the live-coverage era only). Those 99 carry a Half event at
  minute 45 whose `homeScore`/`awayScore` is the HT score (99/99
  consistent: 0 ≤ HT ≤ FT) and Goal events whose count equals the FT
  goal total (99/99). HT goals total 128 vs 279 FT goals in the same
  99 matches (share 0.4588) — a descriptive measurement only, NOT a
  frozen constant: coverage is late-season only. Card events are sparse
  (29 Card events in 99 matches, vs ~300 expected at normal card
  rates), so cards are not a usable target.
- The only target that exists is goals (FT score; HT score in 99/215).
  SOT, corners, cards, total shots, xG do not exist in any payload.

## Gate arithmetic (why no window exists)

- Dev = season-blocked walk-forward. It needs at least one training
  season plus at least one evaluation season. This league has exactly
  one PARTIAL season (2026, 215/240 matches, in progress), which can
  be neither a training season (incomplete) nor an evaluation season
  (no prior season to train on). There is no evaluation season, no
  prior-season climatology, and no complete season at all.
- Virgin: there is no second season to serve as a virgin window. The
  2026 season itself cannot be a virgin: it is the only season, it is
  incomplete, and no arm exists to evaluate against it. A within-season
  round-blocked dev is a program-frame change, not a league decision,
  and is not run under this prereg.
- Even a hypothetical single-season evaluation would be decided by
  noise: at OU 2.5 (over-rate 0.535, n=215) the calibration SE is
  ~3.4pp — over 3× the 1pp clean-PASS threshold — and per-team
  attack/defence rates rest on 26–27 matches per team.
- Precedent: AU-Championship (FotMob 8938) had one COMPLETE season and
  was recorded 0 PASS / 0 FAIL / 5 NOT BUILDABLE. This league is
  thinner still (zero complete seasons).

## Registered decisions

- Arms: **none** (no candidate reaches design).
- Primary lines: **none chosen**.
- Virgin window: **NOT READ for evaluation** for any candidate —
  deliberately unread, because no arm passes (or can pass) a dev gate
  and no virgin season exists. 2026 was tallied at inventory level
  only (n, rounds, dates, season levels in EDA.md) to establish that
  it is partial; no model was fitted or scored against it. 2026
  remains usable only under a future prereg's terms.
- Format rules (frozen for the record): 16 teams, double round-robin,
  30 rounds, 240 matches; no split group, championship/relegation
  round, or playoff phase in the 2026 payloads (rounds 1–27 are a
  single regular phase).
- Halves constants: **none frozen** (HT scores exist for only 99/215
  matches with late-season-only coverage; the measured HT share
  0.4588 is descriptive, not a constant).
- Features X1–X9: **all DROPPED** (see `analysis/FEATURES.md`).
- What ships: **nothing** — no engine, no fitted params, no predictions.

## Verdict

**0 PASS / 0 FAIL / 5 NOT BUILDABLE.** G-UZ, S-UZ, C-UZ, K-UZ, T-UZ are
all NOT BUILDABLE. The league is complete on this verdict. Earliest
gateable revisit: dev on 2026 (once complete) + 2027, virgin 2028 —
needs a fresh preregistration; nothing is scheduled. If FotMob
coverage improves (stats blocks appearing in later seasons), S/C/K/T
become re-assessable on the same revisit — verified from payloads,
never from the index flags.
