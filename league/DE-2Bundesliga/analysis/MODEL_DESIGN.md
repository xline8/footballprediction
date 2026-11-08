# Phase 4 — Model Design: DE-2Bundesliga Candidates

Rules inherited from `league/J1/analysis/MODEL_DESIGN.md`: every
candidate names its production reference, Gate Zero is the
unmodified reference fitted per league, variants come only from
FEATURES.md adopted arms (max 2–3 per candidate), gates are the
program's frozen legs, a FAIL is a complete outcome. Feature
consumption: FEATURES.md.

Shared frame: dev = walk-forward over 2021/2022–2024/2025 (n=1,224,
season-blocked; scored seasons 2022/2023–2024/2025, n=918); virgin =
2025/2026 (n=306, COMPLETE — see DATA_UNDERSTANDING §0 for the
correction of the commissioning brief's "in progress" description),
read ONCE and only for arms passing the dev gate; 2026/2027
(n=99, partial) reserved un-read as the confirmatory window.
Baselines: league base rate (prior-seasons over-rate at the primary
line) and naive trailing-10 (count markets) / climatology (goals).
Calibration rule: |breach| ≤ 1pp clean PASS; ≤ 1 SE PROVISIONAL
PASS; else FAIL. Primary line per candidate = the .5 line whose dev
over-rate is closest to 0.5.

**Format rule (frozen here, before any fitting, and repeated in
every prereg):** all matches are ordinary rows in every fit and
every window — this corpus has no split, no play-off groups, and
no qualification matches (DATA_UNDERSTANDING §1). No phase feature
is used anywhere.

| Candidate | Reference | Primary line (dev over-rate) | Arms |
|---|---|---|---|
| G-DE2 goals | production DC + xG blend (model_v2/model_xg pattern) | OU 2.5 (0.594 pooled) + 1X2 LL/RPS | Gate Zero; SHRINK (thin-data prior: ratings of teams with <6 in-league matches shrunk toward league mean — the sanctioned G-J2-lesson arm); X2 mover offset (direction-specific: up from 3. Liga / down from Bundesliga; offsets estimated inside each fit from transitions completed before the target season, F5); X3 set-play decomposition (on SHRINK, BE form) |
| S-DE2 SOT | model_sot.py v5 | **9.5** (dev 0.450; 8.5 is 0.558 — 9.5 is closer to 0.5) | Gate Zero; RS ratio-shrink (P=20,000); X4 xG/shot quality input (F7 r=0.529). No X6 (dropped, F8 r=0.182) |
| C-DE2 corners | model_corners_v3 | **10.5** (dev 0.444; 9.5 is 0.557 — 10.5 is closer by 0.001) | Gate Zero (X9 covariates); X7 box-touch multiplier |
| K-DE2 cards | model_cards.py | **4.5** (dev 0.434; 3.5 is 0.627) | Gate Zero; X8 referee covariate |
| T-DE2 total shots | shots family (v1/v2/E9, as T-J1) | **27.5** (dev 0.492; 26.5 is 0.562) | A v1 pattern; B v2 level layer; C E9 trailing-r |

Notes:
- G-DE2 has xG for every match — the blend never falls back.
- SHRINK and X2 are both pre-registered here, before any fitting:
  SHRINK is the generic thin-data guard (sanctioned G-J2 lesson);
  X2 is the tier-aware variant this league's two-direction churn
  justifies (F5) — DE-2 is, with J.League, one of the few conveyor
  leagues where the feeder tiers are in the warehouse. X2 stands
  alone on Gate Zero; X3 builds on SHRINK (BE form), so the arms
  stay separable and the both-pass/tie rules stay mechanical.
- X2's down-step is the weak leg of F5 (+0.097/+0.078 on 6 clubs):
  recorded in the design so an X2 failure is read correctly — the
  up-step (−0.360/+0.143 on 9 clubs) is the load-bearing half.
- K-DE2's primary line is 4.5 (DE-2 yellows level 4.27 is the
  highest among the European conveyor leagues bar CH) and its
  team trait (0.558) + referee trait (0.470) are both solid —
  recorded so a K-DE2 failure is read correctly too.
- C-DE2's primary line flips to 10.5 by 0.001 of over-rate — the
  marginal call is recorded here so it is never re-litigated
  after results are seen.
- S-DE2's line is 9.5 and its X4 trait (0.529) is the program's
  strongest — same recording discipline.
- Halves presentation (all markets): FT + 1H/2H via the frozen
  DE-2 constants, presentation only, exactly as J1.
