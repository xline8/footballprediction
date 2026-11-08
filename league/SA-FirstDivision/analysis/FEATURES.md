# Phase 3.5 — Data Processing / Feature Engineering

Consumption rule (J1): `MODEL_DESIGN.md` may use only the features
defined in §1 of this document, plus the architectural components
delimited in §2. Everything in §3 is rejected — explicitly, with its
reason — and may not re-enter through a later phase. A feature not
listed anywhere here is not eligible; adding one requires a new
reliability check and an amendment to this file.

Evidence: `analysis/EDA.md` (dev seasons only: goals 2024/2025,
count targets 2025/2026).

## Global causality contract (applies to every feature below)

1. For a target match M, a feature is computed **only from matches
   with kickoff strictly before M's kickoff**, in the same league
   unless the feature says otherwise. The target match's own payload
   contributes nothing except static fixture facts (the two team ids,
   venue, and — for X8 — the appointed referee's identity).
2. Windows are **trailing** (the team's / referee's most recent N
   matches before M) or **expanding-with-decay** inside a rating fit.
   Window lengths and minimum-sample rules are fixed per candidate in
   its pre-registration; where a window cannot be filled, the feature
   is **NaN and the variant arm that needs it is inactive for that
   match** — never silently filled with the match's own-era average
   computed including M or later matches.
3. Ratio features are **ratios of sums** over the window (as in the
   EDA reliability checks), never means of per-match ratios.
4. Fitted state obeys the production signed-age rule: a state fitted
   on data after M's kickoff is never used for M.
5. Attenuation honesty: EDA reliabilities were measured on
   single-season half-samples (~17 matches per team). Trailing
   windows of 10–25 matches will show **attenuated** versions of the
   same traits. A trait that is NOISE at season scale (r ≈ 0) cannot
   become signal at window scale; a trait that is strong at season
   scale may still fail at window scale — which is what the dev
   walk-forward gate is for.

## §1 Accepted features

### X1 — Blend observation pair (goals-model training input)
- **Definition**: per past match, the pair (goals, team xG) entering
  the Dixon-Coles fit with the production blend weight; goals from
  `header.status.scoreStr`.
- **Availability**: goals — all seasons. xG — **nowhere**: no
  `expected_goals` key exists in any of the 712 payloads, and the
  shotmap is empty in all of them. The blend therefore runs
  **goals-only throughout** (the reference blend's documented
  fallback), in every fit and every window.
- **Justification**: F1 (levels) + the production blend's own gate
  history. The goals-only fallback is the reference behaviour, not a
  variant.

### X2 — Mover tier offset (prior for promoted / relegated clubs)
- **Verdict: DROPPED** (see §3, R14). Not defined here because no
  estimable transition history exists in this corpus.

### X3 — Set-play xG share and rate (trailing)
- **Verdict: DROPPED** — data absent. No xG splits exist in any era
  (no `expected_goals_set_play`, no `expected_goals` at all).

### X4 — xG per shot (trailing)
- **Verdict: DROPPED** — data absent. The shotmap is empty in all
  712 payloads; there is no per-shot `expectedGoals` to sum.

### X5 — Trailing target-rate means (naive / ensemble components)
- **Definition**: the team's trailing-10 mean of the candidate's own
  target (SOT, corners, event-unified yellows, total shots) and the
  corresponding conceded mean — the naive component of the reference
  architectures (v5's ensemble; corners/cards/shots analogues) and
  the harness's naive baseline. Sources: Phase 2 columns
  (`ShotsOnTarget_*`, `corners_*`, `total_shots_*`, unified
  `yellow_*`).
- **Window**: trailing 10 team matches, strictly pre-match. If fewer
  than 6 of the 10 carry the stat, the feature is NaN for that match.
  In the count-markets dev season this bites at the season start (a
  newcomer's first matches have no trailing history by construction).
- **Availability**: SOT/corners/total-shots/yellows — 2025/2026 and
  2026/2027 only (the stats era). The 2024/2025 season contributes
  no trailing target history for any count market.
- **Justification**: F2 (target traits reliable: SOT-for r=0.688,
  corners-for 0.735, shots-for 0.808; yellows-for r=0.156 — the
  yellows leg of X5 is weak by the same evidence, and the K-SAFD dev
  gate will judge it) + the reference architectures' own validation
  history.

### X6 — Attacking xGOT per shot (trailing, era-guarded)
- **Verdict: DROPPED** — data absent. No `expectedGoalsOnTarget`
  exists anywhere in the corpus.

### X7 — Opp-box touches for / against (trailing)
- **Definition**: trailing means of the stats-feed
  `touches_opp_box` (`content.stats.Periods.All`) for the team
  (`_for`) and conceded to opponents (`_against`), per match.
- **Window**: trailing means; minimum 8 window matches with the
  stat, else NaN.
- **Availability**: 2025/2026 and 2026/2027 only (the stats era).
- **Justification**: F2 (**SIGNAL**: for-trait split-half r=0.790,
  against-trait r=0.735) + F5 (per-match corr with corners 0.537,
  above J1's 0.471). Consumed by C-SAFD's territorial-multiplier arm.

### X8 — Referee yellow rate (trailing)
- **Verdict: DROPPED** — not measurable. 0 referee names in both
  dev seasons (F6). The 93/94 coverage in the unread 2026/2027
  cannot create a dev-estimable trait.

### X9 — Reference territorial covariates (corners Gate Zero arm)
- **Definition**: trailing means of stats-feed `BallPossesion` and
  `big_chance` for/against — production `model_corners_v3`'s
  multiplier covariates, carried unchanged so Gate Zero is the true
  production pattern, not a straw man.
- **Window/availability**: trailing means, min-8 rule; stats era
  only (2025/2026, 2026/2027).
- **Justification**: production adoption evidence; for the record,
  big-chances-for is reliable on this corpus too (split-half r=0.624)
  and possession-for r=0.781 (F2).

## §2 Architectural components — explicitly NOT features

- **Ratings, home advantage, Dixon-Coles rho, NB sizes** are fitted
  parameters of the shared architecture (justified by F1/F2 at the
  architecture level), not covariates; they are estimated by the
  fit, under the signed-age rule.
- **v5's Beta-Binomial on-target ratio** is a *fitted latent
  component* of the S-SAFD reference architecture. It is not a
  trailing covariate, and its presence in Gate Zero is exactly what
  S-SAFD's ratio-shrinkage arm tests (F2). This does **not** license
  a standalone trailing on-target-rate covariate — that object is
  R4 below.
- **League half-share constants** (SOT 0.4540, corners 0.4678, total
  shots 0.4557, event yellows 0.4010 — all measured on 2025/2026
  regular played) are frozen constants for report-style splits, per
  F3. They are not features, carry no team dimension, and may not be
  "improved" into per-team or per-match quantities. Goals has no
  constant (F3): G-SAFD presents FT only.
- **League base rates / naive baselines** belong to the evaluation
  harness, not to any model.

## §3 REJECTED features (explicit; reason recorded for each)

| # | Feature | Verdict / reason |
|---|---|---|
| R1 | Team first-half shares (goals, SOT, corners, shots, yellows) | **NOISE** — F3: true variance ≈ 0 for all four measured markets (0.0 / 0.0105 / 0.0 / 0.0); goals unmeasurable in dev. The halves book stays closed. |
| R2 | Trailing finishing (goals − xG) | **NOT TESTABLE** — no xG exists in any era. Ineligible, not "promising". |
| R3 | Trailing conversion (goals / shot) as a covariate | **REJECTED** — outcome-contaminated (prices in the same finishing luck as R2); dominated by shot volume + SOT. No reliability evidence in this corpus. |
| R4 | Standalone trailing on-target rate (SOT / shots) | **REJECTED** — split-half r=0.428 on a single season (n=18 teams, 17v17 halves; CI wide, includes ~0.1) vs J1's career-pooled r=0.06. Not strong enough to license a standalone covariate arm; the RS arm is the ratio test. Distinct from v5's internal ratio component (§2). |
| R5 | Defensive xGOT per shot | **NO DATA** — no xGOT anywhere. |
| R6 | Lineup / absence features (star-absence, minutes-weighted XI strength, top-scorer availability) | **CLOSED** — program-level V10 verdict (no effect) + no lineup data in 2024/2025. The agreed reopening standard (new reliability evidence) was not met. |
| R7 | Top-shooter concentration share as a team trait | **NO EVIDENCE** — never reliability-tested as a trait. Ineligible until its own EDA-grade check exists. |
| R8 | Formation / coach features | **NO EVIDENCE** — present in the payload (lineups 2025/2026+) but no reliability check was run; ineligible, not "promising". |
| R9 | Standings position, h2h, teamForm snapshots | **LEAKAGE** — `content.table`/`h2h` are post-match snapshots of the target match itself. |
| R10 | Attendance | **LEAKAGE / NOT PRE-MATCH** — the payload's figure is the actual crowd, known only after the match. |
| R11 | First-goal and other game-state traits | **NOT PRE-MATCH** — descriptive in-match facts only. |
| R12 | Red-card rates (as target or covariate) | **REJECTED** — 0.28 per match is a rare-event count; no reliability evidence; the production cards design excludes reds as a target as well. |
| R13 | Momentum | **NOT PRE-MATCH** — an in-match/live quantity in this payload. |
| R14 | X2 mover tier offset | **DROPPED** — no estimable transition history: 6 movers per boundary but no tier-3 / Pro-League data inside this corpus to estimate an offset from. The SHRINK arm (G-SAFD) is the sanctioned thin-data treatment instead. |

## §4 Consumption map (design ← features)

| Candidate | Base inputs | Variant-arm features |
|---|---|---|
| G-SAFD | X1 (goals-only) | SHRINK (sanctioned G-J2-lesson arm, §2-adjacent) |
| S-SAFD | X5 (SOT naive + ratings observations) | RS ratio-shrinkage (§2) |
| C-SAFD | X5 (corners naive), X9 (Gate Zero multiplier) | X7 (box-touch multiplier arm) |
| K-SAFD | X5 (yellows naive + ratings) | — (X8 dropped) |
| T-SAFD | X5 (shots naive + ratings observations) | — (shots-family arms A/B/C are architectural variants, not features) |
