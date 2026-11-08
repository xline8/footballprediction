# Features and decisions — Cyprus 2. Division

J1 feature template (X1–X9), decided per feature on THIS league's
data. A feature is adopted only if the data exists AND its
reliability check passes in this league.

- **X1 xG blend — DROPPED**: no xG in any season. Goals fit is
  goals-only throughout (the reference blend's documented
  fallback).
- **X2 cross-tier prior — ADOPTED as a gated variant arm only**:
  sibling CY-1Division exists in the warehouse and is already built
  + joined to the runner, so relegated-in movers are identifiable
  by team id. Measured gap (EDA F4, pre-virgin transitions, n = 8
  team-seasons): attack +0.08, defence −0.21 goals/match — small,
  defence-led. The arm applies the measured offset to a club whose
  immediately-preceding season was in CY-1Division; the gate
  decides whether it ships. Brand-new ids get no offset (EDA F4:
  they are league-average on arrival).
- **X3 set-play — DROPPED**: no set-play xG.
- **X4 xG/shot — DROPPED**: no xG or shotmap.
- **X5 naive trailing-10 — NOT APPLICABLE to the goals candidate**:
  the Dixon-Coles reference has no trailing-mean component, and the
  dev harness scores against climatology (the CY-1Division goals
  harness convention). No trailing-10 baseline is scored for goals.
- **X6 xGOT — DROPPED**: absent.
- **X7 box touches — DROPPED**: absent.
- **X8 referee — DROPPED**: empty in all 1,210 payloads.
- **X9 territorial — DROPPED**: no possession / big-chance keys
  (no stats feed at all); not applicable to the goals candidate.

All phases are modelled as ordinary matches, phase is retained as
a flag, and no phase feature is used. Halves constant (goals):
**0.4351** (EDA F3) — presentation only, never a feature.
