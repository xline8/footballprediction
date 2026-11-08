# Pre-registration — S/C/K/T NOT BUILDABLE (AM-PremierLeague)

Frozen: 2026-11-10, before any fitting. Branch `build/am-premier-league`.
Design authority: `league/AM-PremierLeague/analysis/MODEL_DESIGN.md` §2
and `EDA.md` F13; coverage per `DATA_UNDERSTANDING.md` §2.

This prereg is written in Phase A, before any fitting, so that the
not-buildable verdict for these four markets is on record before dev
results exist for goals. No engine, dev run, virgin read, or verdict
exists for any of them, and none will be created in this build.

## S-AM (shots on target) — NOT BUILDABLE

- Target does not exist: team stats are null in 881/881 payloads
  (no `ShotsOnTarget` key anywhere) and the shotmap shot list is
  empty in 881/881. No SOT value exists in any season, so there
  is no training target and no valid virgin window containing it.
- Template conditions (a) target exists AND (b) virgin window
  contains the target: both fail.

## C-AM (corners) — NOT BUILDABLE

- Target does not exist: no `corners` key in any payload (stats null
  881/881); no corner events exist in the event feed (only
  Goal/Half/Card). Same double failure as S-AM.

## K-AM (cards) — NOT BUILDABLE

- Target does not exist in usable form: no stats feed (no
  `yellow_cards` anywhere); the event feed contains 186 Card events
  total, all YellowRed (51) or Red (135) — **0 Yellow cards** in the
  whole corpus. A reds-only count (0.21/match) is a rare-event count
  with no reliability evidence and no production analogue; the
  production cards design excludes reds as a target. Referee data,
  the usual cards covariate, is also absent (Referee text empty
  881/881). Lineups are absent too (0/881 with real content — 16
  unavailable shells).
- Template conditions (a) and (b): both fail.

## T-AM (total shots) — NOT BUILDABLE

- Target does not exist: no `total_shots` key (stats null) and the
  shotmap is empty in 881/881. Same double failure as S-AM.

## Consequence

The AM-PremierLeague build is a single-candidate build (G-AM only).
If FotMob later supplies stats/shotmap coverage for this league, the
four markets would need a fresh six-step pass and their own preregs;
nothing in this build prejudges them.
