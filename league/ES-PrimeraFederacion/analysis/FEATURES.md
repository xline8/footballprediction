# Phase 3.5 — Feature Engineering (J1 template X1–X9, judged on ES-PrimeraFederacion data)

Consumption rule and causality contract are inherited verbatim from
`league/J1/analysis/FEATURES.md` (trailing/expanding windows only,
strictly pre-match, ratio-of-sums, NaN ⇒ arm inactive, never imputed).
Each verdict was re-measured on this league (EDA), or dropped on
availability where the data does not exist in any season. Team
identity is keyed on FotMob team_id throughout (Phase 2 rule 9);
the only name-keyed test (X2 membership in EDA) uses
accent-normalised names, verified 1:1 against ids — and the engine
itself keys movers on team_id (MODEL_DESIGN §2).

| # | Feature (J1 analogue) | PF verdict | Evidence |
|---|---|---|---|
| X1 | Blend observation pair (goals + xG) | **DROPPED** (no xG anywhere) | `expected_goals` exists in 0 of 4,081 matches — not era-dead, never-born. There is no xG era in this league at all. The goals fit is therefore **goals-only** — the production reference's own documented fallback (J2 precedent), not a modified Gate Zero |
| X2 | Mover tier offset | **ADOPTED** (arm) | F4: upper adjacent tier in the warehouse (LaLiga2 id 140); lower tier (Segunda Federación) not in the warehouse, identified by absence. Exactly 4 + 10 movers every season. Entry GD +0.231 (from LaLiga2) / −0.065 (from below) per match. Frozen magnitudes vs mu 1.1581 (dev entry seasons only): from-LaLiga2 ΔGF +0.081 / ΔGA −0.150; from-below ΔGF −0.054 / ΔGA +0.011. Applied at prediction time in the entry season only, ENGCH X2 formulation; membership keyed on team_id from warehouse payloads in the engine |
| X3 | Set-play xG share/rate (trailing) | **DROPPED** (no xG anywhere) | F5: no xG splits in any season. Not measurable, not built |
| X4 | xG per shot (trailing) | **DROPPED** (no shotmap) | F6: shotmap empty in 4,081/4,081 payloads |
| X5 | Trailing target-rate means (naive/ensemble) | **ADOPTED** (embodied in Gate Zero) | F1: goals-for r=0.296, goals-against r=0.376 (chronological split-half, n=160 team-seasons) — modest but real. The DC's expanding-window fit IS the trailing-goals mechanism here; no separate trailing covariate arm is built, and the naive baseline for the gate is the expanding climatology, not a trailing-10 |
| X6 | Attacking xGOT/shot (era-guarded) | **DROPPED** (no shotmap) | F7: xGOT does not exist in any season; no era guard can create a window |
| X7 | Opp-box touches for / against (trailing) | **DROPPED** (no stats) | No stats feed in any season; the key does not exist |
| X8 | Referee yellow rate (trailing) | **DROPPED** (double) | F8: referee text empty in 4,081/4,081 payloads (0% coverage) AND no cards target exists to attach it to |
| X9 | Reference territorial covariates (possession, big chances) | **DROPPED** (no stats) | Possession / big-chance keys do not exist in any payload |

## Halves constants (frozen, DEV seasons only, event-derived)

goals **0.4301**. SOT / corners / total shots / cards: none (markets
not buildable). Presentation only, exactly as J1. Note the constant
is event-derived (Goal-event times; complete-goal-event matches
only), because no stats period splits exist — and it is frozen on
dev seasons only, unlike the ES-LaLiga2 precedent, which measured
its constants on an era including the virgin.

## Rejected (inherited from J1 §3, re-affirmed on PF data)

- Team half shares (all stats): NOISE (F3, true SD 0.0) — frozen
  constants only.
- Standalone trailing on-target rate / finishing as covariates
  (no SOT data exists to compute them from).
- Lineup/absence (CLOSED per program history), standings/h2h
  snapshots (leakage), red cards as target (rare-event count, and
  the card feed is a sparse subset anyway).
- Phase (regular/play-off) as a feature: play-off rounds are
  ordinary rows; no phase covariate anywhere.
- Group as a feature: the two groups share one rating pool in Gate
  Zero (MODEL_DESIGN §1). A group-split fit was considered and
  rejected — it would diverge from the unmodified reference and
  play-off predictions would need cross-model calibration with no
  shared scale. Within-group predictions are invariant to the
  per-group shift in any case.
- Any xG/shotmap-derived covariate for a *future* arm: eligible
  only if FotMob's coverage of this league changes (stats/shotmap
  appear in a full season). Recorded so the drops are not mistaken
  for permanent rejections of the features themselves.
