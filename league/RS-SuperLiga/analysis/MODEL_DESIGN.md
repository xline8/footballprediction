# Step 6 — Model Design: RS-SuperLiga

Design consumes only step-5 features (FEATURES.md). Reference patterns are the FI-Veikkausliiga
preregs (`PREREG_G_FI.md`, `PREREG_T_FI.md`); where RS diverges from FI, the divergence is
forced by this league's EDA and is stated per candidate below.

## The era break, stated plainly

The stats feed does not exist at all in the dev era (2021/2022–2024/2025: 0 stats rows in
1,192 matches). It exists only in the virgin season itself (2025/2026: 296/296 matches, 36 keys).
The expected consequence is that **S/C/K/T have no stats-era dev data at all — their targets
exist only in the virgin season itself — so they cannot pass a season-blocked dev gate**.
A dev gate can only validate an arm against the same quantity it would ship against, and there
is no dev season carrying that quantity: not one season (unlike FI, which had one rich dev
season for T-FI and still ruled it not-buildable). Each of S/C/K/T is therefore
**not-buildable**, following the FI `PREREG_T_FI.md` precedent: this is a feasibility verdict
recorded before any fitting, not a gate FAIL. Nothing is fitted for them, and the virgin is
not read for them. Only G-RS — goals, the one target that exists in every season — is built.

## Feasibility matrix

| Candidate | Target in dev? | Target in virgin? | Verdict |
|---|---|---|---|
| G-RS goals | yes, all 1,192 matches (FT scores) | yes, 296 | **BUILDABLE** — Dixon-Coles goals-only |
| S-RS SOT | no (0 stats rows) | yes, 8.831/match (inventory) | **NOT BUILDABLE** — no dev data; no dev gate possible |
| C-RS corners | no (0 stats rows) | yes, 9.003/match (inventory) | **NOT BUILDABLE** — no dev data; X7 and even the possession fallback are virgin-only |
| K-RS cards | no usable target (event feed YellowRed-only, 0.041–0.120/match) | yes, but a different quantity (events 4.662, stats 4.230) | **NOT BUILDABLE** — no target with the same meaning in dev and virgin |
| T-RS total shots | no (0 stats rows) | yes, 25.084/match (inventory) | **NOT BUILDABLE** — no dev data and no dev definition check possible (FI T-FI precedent, zero rich dev seasons) |

Windows frozen for the built candidate: virgin = **2025/2026** (complete, 296 matches, last match
2026-05-24 — read ONCE, only for dev-passing arms). Dev = season-blocked walk-forward as tabled.
Reserve 2026/2027 is untouched.

| Candidate | Reference (Gate Zero) | What stays identical | What this league's EDA justifies changing | Variant arms (pre-registered) | Warm-up | Dev scored | Primary line |
|---|---|---|---|---|---|---|---|
| G-RS goals | Production DC pattern, goals-only (X1 fallback), per `PREREG_G_FI.md` (14 sweeps, damping 0.7, +0.25 smoothing, home init 0.28, MAXG = 10, production tau, rho grid (0.0, −0.05, −0.10, −0.15) by goals log-likelihood, decay HL = 270 days) | Everything in the reference except the two changes in the next column | (1) **Qualification rows excluded from fitting**: the 8 cross-tier relegation play-off ties (2021/2022 + 2022/2023) pit Super Liga clubs against Prva Liga clubs with no in-corpus history; FI had no such rows, RS does — the exclusion is documented in DATA_UNDERSTANDING.md and `eda_summary.json: qualification_matches`, never silent. (2) **X2 entrant identification uses regular-phase teams** (the plain-absence rule is contaminated by tier-2 qualification opponents — EDA.md F4) | SHRINK (thin-data prior, per the G-J2 lesson: at prediction time a team with n < 6 prior in-league matches has a *= n/6, d *= n/6); X2 (SHRINK + entrant offset, see below) | 2021/2022 (300 matches; 296 league-member) | 2022/2023–2024/2025 (n = 892 rows; 888 league-member after the qualification exclusion) | 1X2 LL/RPS + OU 2.5 |
| S-RS SOT | Production v5 pattern (FI `PREREG_S_FI.md`) | — | — | — none | — | — | NOT BUILT: SOT exists only in the virgin (8.831/match); no dev SOT, no X4 (no shotmap, no xG); a v5 arm cannot be dev-evaluated |
| C-RS corners | Corners_v3 pattern (FI `PREREG_C_FI.md`) | — | — | — none | — | — | NOT BUILT: corners exist only in the virgin (9.003/match); X7 dropped (touches virgin-only) and the FI possession-only fallback is also unavailable (possession virgin-only) |
| K-RS cards | Production cards pattern on event yellows (FI `PREREG_K_FI.md`) | — | — | — none | — | — | NOT BUILT: no usable yellows target — dev event feed is YellowRed-only (0.041–0.120/match, r = 0.060) and the stats feed exists only in the virgin and undercounts events by 0.432/match; X8 dead (referee names absent in dev) |
| T-RS total shots | NB level model, arms A/B/C (DK/FI precedents) | — | — | — none | — | — | NOT BUILT: total_shots exists only in the virgin (25.084/match); no dev series, so no definition check and no season-blocked dev gate — the FI T-FI precedent with zero (not one) rich dev seasons |

## G-RS arms (detail)

1. **Gate Zero** — the unmodified reference above, fitted on league-member rows only
   (phase != qualification).
2. **SHRINK** — Gate Zero plus the sanctioned G-J2-lesson change (see table).
3. **X2** — SHRINK plus the entrant offset: a club whose previous completed season was NOT
   in the Super Liga regular phase (entrant, identified in-corpus by absence from the previous
   season's regular-phase teams — RS is tier 1, entrants are promoted clubs; no tier-2 corpus
   is built in-system) enters with its lambdas tilted — its scoring lambda multiplied by
   exp(g), its conceded lambda by exp(c), where (g, c) are the mean (GF diff, GA diff) of all
   entrant transitions completed BEFORE the predicted season, measured in the RS corpus itself
   (each entrant's first-season GF/GA per match minus that season's league team mean; dev
   measurement: GF −0.326, GA +0.242 over 7 transitions, `eda_summary.json:
   x2_entrant_gf_ga_diff_vs_league_team_mean_dev`); if fewer than 3 completed transitions
   exist, the offset is 0. Multipliers clamped to [0.8, 1.25]. The tilt applies only in the
   entrant's first Super Liga season. (Divergence from FI's X2, forced by EDA: the entrant
   definition uses regular-phase teams, because the plain-absence rule here catches tier-2
   qualification opponents.)

## Gate legs (identical program-wide, frozen in the prereg)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat BOTH baselines (climatology:
prior-seasons pooled outcome rates + OU2.5 over-rate; naive trailing-10), and OU2.5 LL must
beat the base-rate baseline, else the arm is dead and the virgin is NOT read for it; if Gate
Zero fails dev, variants are moot. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's
AND ≤ climatology's; (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for
home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is
recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate
Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero
and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it
ships; if none passes, G-RS verdict is FAIL and nothing ships. Ties → simpler arm
(Gate Zero, SHRINK, X2). Halves presentation via the frozen goals constant 0.4606
(EDA.md F3; to be frozen in Phase 6 config). There is no SOT/corners/shots/cards product,
and no halves constant exists for them.
