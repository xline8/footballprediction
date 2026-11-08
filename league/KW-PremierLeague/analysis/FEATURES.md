# KW-PremierLeague — Features (Step 5)

Template features are adopted only if their data exists AND their
reliability passes in EDA. Verdicts:

- **X1 (xG blend) — goals-only fallback.** No `expected_goals*` key
  in any of the 711 payloads and no shotmap, so there is no xG to
  blend in any era. The Dixon-Coles observation is goals-only in
  every match (the documented X1 fallback, as in BY/FR/CN).
- **X2 (entrant handling) — ADOPTED** (EDA F4): 8 dev transitions,
  mean GF diff −0.390 (7/8 negative), mean GA diff +0.404 (5/8
  positive); offsets clamped to ±log(1.25)/log(0.8) bounds. The arm
  exists as the third G arm; the rule is recomputed pre-season from
  completed transitions only.
- **SHRINK (G-J2 lesson) — adopted as an arm** (programme standard):
  teams with n < 6 prior in-league matches have attack/defence
  exponents scaled by n/6 at prediction time. Expected near-inert
  under season-blocked prediction here (teams present in a prior
  season have ≥14 prior matches — entrant seasons can be short
  because of the split-phase format, min observed 14; teams with no
  fitted rating sit at league mean with exponents 0.0, where the
  scaling is a no-op). Run and reported anyway; the gate decides.
- **X3 (set-play share) — dropped: no stats feed in any season.**
- **X4 (on-target ratio) — dropped: no SOT data in any season.**
- **X6 (shot volume) — dropped: no shot data in any season.**
- **X7 (box touches / territory) — dropped: no stats feed.**
- **X8 (referee) — dropped: referee named in 0/711 matches.**
- **X9 (keeper saves) — dropped: no stats feed.**

Halves: the only legal halves model is the frozen constant —
goals 1H share **0.4411** (EDA F3, from 2024/2025 event matches
only; thin base flagged). No halves constants for S/C/K/T.
