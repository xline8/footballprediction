# Step 4/5 — Features: Indonesia Super League

J1 template X1–X9 audited against this league's data. The global
causality contract from the J1 template applies unchanged (features
use only matches strictly before kickoff; ratio features are ratios of
sums; unfitted windows are NaN and the arm is inactive, never filled).

## Adopted

- **X5 — Trailing target-rate means (ADOPTED, cards only).**
  Trailing-10 team means of event-unified yellows for/against, the
  naive component of the cards reference architecture and the harness
  baseline. Reliability in this league: yellows for r=0.402, against
  r=0.338 (within-season split-half) — modest but real. Window rule:
  trailing 10 team matches on events_complete rows only; a window
  match with a truncated feed contributes nothing (it is skipped, not
  counted as zero cards). SOT/corners analogues are moot — those
  candidates are not buildable.
- **Ratings architecture (not a feature).** Dixon–Coles attack/defence
  ratings + home advantage + rho for goals; decayed venue-split
  yellow ratings for cards — fitted parameters of the reference
  patterns, per the template's §2 boundary.

## Dropped (each with its measured reason)

- **X1 — xG blend pair: DROPPED.** `expected_goals` does not exist in
  any of the 1,620 payloads. The goals model is goals-only by
  construction (the reference blend's documented fallback).
- **X2 — Mover tier offset: DROPPED.** The offset must be estimated
  from the other tier's matches; Indonesia's Liga 2 (FotMob 10056) is
  empty in the warehouse, so no prior-tier observations exist. The
  promoted-team problem is instead addressed by the pre-registered
  SHRINK arm (template-sanctioned), which needs no external data.
- **X3 — Set-play xG share: DROPPED.** No xG of any kind exists.
- **X4 — xG per shot: DROPPED.** Shotmap is empty in all 1,620
  payloads and no xG exists.
- **X6 — xGOT per shot: DROPPED.** No shotmap, no xGOT.
- **X7 — Opp-box touches: DROPPED.** The `touches_opp_box` key does
  not exist in this league's stats feed (only BallPossesion,
  total_shots, ShotsOnTarget, corners ever appear).
- **X8 — Referee yellow rate: DROPPED.** Referee identity is absent:
  `infoBox.Referee.text` is empty in 1,620/1,620 payloads. No
  reliability check can be run. (Operational note: with no appointed-
  referee field in the feed at all, this feature could not be served
  live either.)
- **X9 — Territorial covariates (possession / big chance): DROPPED.**
  `big_chance` does not exist. Possession exists and is reliable
  (r=0.672), but only inside the stats era (ends Oct 2023); it has no
  values in the virgin season or in any future live fixture, so it
  cannot serve a shipped model. Its only possible consumers (corners/
  SOT) are not buildable anyway.

## Rejected (template §3 items that arise here)

- R1 team first-half shares: NOISE — EDA variance decomposition gives
  true variance ≈ 0 for goals and yellows. Frozen league constants
  only (goals 0.434, yellows 0.385; recent-era measurement, EDA).
- R9 standings/h2h snapshots, R10 attendance (null in payloads),
  R13 momentum (`content.momentum` is false throughout): leakage /
  not pre-match, excluded.
- R12 reds as a target: the frozen cards target is unified yellows
  (RU precedent); reds are kept as audit columns only.

## Halves presentation

Goals and cards ship FT + 1H/2H presentation via the frozen constants
above, from the event-time source documented in Step 1 §5. SOT,
corners and total shots have no halves source (no splits, no events)
and are FT-only by construction (moot — not buildable).
