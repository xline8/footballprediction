# Step 5 — Features: VE-PrimeraDivision

Decisions use only the measured EDA and the stated window discipline.
Consumption rule (as J1): `MODEL_DESIGN.md` may use only the features
defined in §1 below, plus the architectural components in §2.
Everything in §3 is rejected and may not re-enter through a later
phase. The global causality contract of J1 FEATURES §1 applies
unchanged: features use only matches with kickoff strictly before the
target match, trailing windows or expanding-with-decay fits, ratios of
sums, never the target match's own payload except static fixture facts.

## §1 Accepted / dropped features

| feature | decision | evidence / reason |
|---|---|---|
| X1 goals observation pair | ADOPTED, degraded to goals-only | Scores complete in all 1,497 rows. No xG key exists in any season (0 expected_goals keys, 0 non-empty shotmaps), so the production blend's documented goals-only fallback applies to 100% of observations. |
| X2 parent-tier mover prior | DROPPED | No second-tier Venezuelan corpus exists in the warehouse (only league 339). |
| X3 set-play xG share/rate | DROPPED | No xG splits exist (0 matches with an xG key). |
| X4 xG per shot | DROPPED | 0 non-empty shotmaps. |
| X5 trailing target-rate means | ADOPTED | SOT/corners/total-shots/possession exist in all 343 stats-era matches; stats yellows in the 288 full-feed matches (62 in 2025 + 226 in 2026). Trailing-10 with the min-6 rule (feature NaN where fewer than 6 of the 10 carry the stat — this absorbs the 2025 reduced-feed matches for K). |
| X6 attacking xGOT per shot | DROPPED | No shotmap or xGOT field. |
| X7 opp-box touches | DROPPED | `touches_opp_box` is ABSENT (0 matches carry the key). The C-VE variant arm that J1/BO built on X7 therefore does not exist here. |
| X8 referee yellow rate | DROPPED | Referees named in only 87/233 matches in 2025 and 145/227 in 2026, and yellows exist only in the stats era (2025 Clausura + 2026) — no multi-season reliability check is runnable, and whether appointments are published pre-match in the live pipeline is unknown. |
| X9 territory/chance (corners Gate Zero) | ADOPTED, possession-only | Possession is present throughout the stats feed and reliable (split-half pooled r=.655). `big_chance` is DEAD: the key exists but reads 0 in all 288 full-feed matches (nonzero in 0/288), so the big-chance covariate is a constant 0 in Gate Zero and contributes nothing. |
| SHRINK (goals variant) | ADOPTED for G-VE variant | Sanctioned G-J2 lesson: shrink unseen/new-team ratings to a prior to limit opener extremes. |

Frozen constants (presentation only, from EDA): goals 1H share .4478,
SOT .4651, corners .4669, total shots .4662, stats yellows .3900.
True variance of the per-match 1H share is ≈ 0 for goals (−.0004),
SOT (−.0002) and total shots (+.0003), and small-positive for corners
(+.0042) and yellows (+.0056) — the constants stay frozen, never
fitted per team.

League-specific notes:

- The on-target rate is NOISE here (split-half r=−.519 in 2025,
  +.015 in 2026, −.300 pooled, n=14 teams/season) — unlike BO, where
  it was signal (r=.613). S-VE's RS arm is therefore NOT an
  EDA-motivated feature arm; it is the standard v5-component test
  (J1 FEATURES §2): the Beta-Binomial on-target ratio is a fitted
  latent component of Gate Zero, and the harder prior (20,000) tests
  that component. Since the rate is noise, hardening the prior toward
  the league mean is the direction the evidence points — RS may help
  or be neutral, and it ships only if it beats Gate Zero on dev AND
  virgin.
- Trailing finishing (goals/shot) was not reliability-tested and
  cannot be: there is no xG, and the goals/shot ratio is
  outcome-contaminated (J1 R3). It stays rejected.
- Team trait reliabilities (pooled stats era, split-half): goals
  for/against .461/.336, SOT .274/.359, corners .615/.264, yellows
  .156/.587, total shots .558/.395, possession .655. Corners-for,
  total-shots-for and possession are the usable signals; yellows-for
  is weak (the against-trait is the signal — opponents draw cards).

## §2 Architectural components — explicitly NOT features

Ratings, home advantage, Dixon-Coles rho, NB sizes are fitted
parameters of the shared architectures, not covariates. v5's
Beta-Binomial on-target ratio is a fitted latent component of the
S-VE reference architecture (its harder-shrinkage arm is the RS arm
above). League half-share constants are frozen presentation constants.
League base rates / naive baselines belong to the evaluation harness.

## §3 REJECTED features (explicit; reason recorded for each)

| # | Feature | Verdict / reason |
|---|---|---|
| R1 | Team first-half shares (goals, SOT, corners, shots, yellows) | NOISE — true variance ≈ 0 for goals/SOT/shots, small-positive for corners/yellows; the halves book stays closed. |
| R2 | Trailing finishing (goals − xG) | IMPOSSIBLE — no xG exists. |
| R3 | Trailing conversion (goals / shot) as a covariate | REJECTED — not reliability-tested here; outcome-contaminated (J1 R3). |
| R4 | Standalone trailing on-target rate (SOT / shots) | NOISE — split-half r=−.300 pooled. Distinct from v5's internal ratio component (§2). |
| R5 | Defensive xGOT per shot | IMPOSSIBLE — no shotmap/xGOT. |
| R6 | Lineup / absence features | CLOSED — J1 V10 protocol result stands; no new reliability evidence in this league. |
| R7 | Top-shooter concentration share | NO EVIDENCE — never reliability-tested as a trait. |
| R8 | Formation / coach features | NO EVIDENCE — no reliability check run; ineligible, not "promising". |
| R9 | Standings position, h2h, teamForm snapshots | LEAKAGE — post-match snapshots of the target match itself. |
| R10 | Attendance | LEAKAGE / NOT PRE-MATCH — actual crowd, known only after the match. |
| R11 | First-goal and other game-state traits | NOT PRE-MATCH — descriptive in-match facts only. |
| R12 | Red-card rates (as target or covariate) | REJECTED — rare-event count; no reliability evidence; the production cards design excludes reds as a target. |
| R13 | Event-feed cards as target or covariate | REJECTED — pre-2026 event cards are ~absent (2025 Clausura: 3 event-unified vs 370 stats yellows, agreement 0/62) and 2026 events overcount stats (1,388 vs 1,276; exact 155/226), plausibly staff/bench cards. Stats yellows are the K target. |
| R14 | Post-hoc rescue arms | FORBIDDEN — a candidate that fails its dev gate gets no rescue arm in the same prereg. |
| R15 | Big-chance covariate as signal | DEAD — `big_chance` reads 0 in all 288 full-feed matches; constant, carries no information. (Kept inside Gate Zero's X9 only as the production pattern's void covariate.) |

## §4 Consumption map (design ← features)

| Candidate | Base inputs | Variant-arm features |
|---|---|---|
| G-VE | X1 (goals-only) | SHRINK |
| S-VE | X5 (SOT naive + ratings observations) | RS (v5-component test, §2) |
| C-VE | X5 (corners naive), X9 (possession live, big-chance void) | — (X7 impossible) |
| K-VE | X5 (stats-yellows naive + ratings) | — (X8 dropped) |
| T-VE | X5 (total-shots naive) | — (v1/v2/E9 are architecture arms, not features) |
