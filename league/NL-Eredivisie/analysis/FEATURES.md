# Phase 3.5 — Data Processing / Feature Engineering (NL-Eredivisie)

The J1 template (X1–X9) applied to this league. **Consumption rule:
`MODEL_DESIGN.md` may use only the features defined in §1, plus the
architectural components delimited in §2. Everything in §3 is
rejected — explicitly, with its reason.** The global causality
contract is J1's, unchanged: features for a target match M use only
matches with kickoff strictly before M; windows are trailing or
expanding-with-decay; ratio features are ratios of sums; where a
window cannot be filled the feature is NaN and the arm that needs
it is inactive for that match — never silently filled.

## §1 Accepted features (template verdicts for THIS league)

### X1 — Blend observation pair (goals-model training input) — ADOPTED
Per past match, (goals, team xG) entering the Dixon-Coles fit with
the production blend weight; xG = stats-feed `expected_goals`.
Availability: **all seasons, 100%** (no goals-only era, unlike J1).
Justification: F11 (goals/xG 1.01–1.07 per full season) + F1/F2.

### X2 — Mover / newcomer tier offset (prior for promoted clubs) — ADOPTED
For a club whose previous completed season was in the Eerste
Divisie (it appears in this corpus in season S but not S−1), its
rating prior at season entry is shifted by the F4 offset magnitudes
measured on this corpus: attack **−0.45** goals/match, defence
**+0.26** goals/match (pooled over the four complete transitions;
the offset is applied as a log-ratio shift against the decayed
league team mean, exactly as in G-J1's X2 arm). The offset used for
season S is the pooled historical magnitude — a design constant
frozen in the prereg, not re-estimated on S. Availability: every
season has exactly 3 newcomers. Justification: F4 (**SIGNAL**,
attack side strong, defence side noisier — recorded honestly; the
arm is gated, Gate Zero is the fallback).

### X3 — Set-play xG share and rate (trailing) — ADOPTED
`sp_share = Σ expected_goals_set_play / Σ expected_goals`,
`sp_rate = Σ expected_goals_set_play / matches` over the trailing
window (ratio of sums; min 8 window matches with xG, else NaN).
Availability: all seasons (xG splits are in the stats feed
throughout). Justification: F5 (**SIGNAL-CANDIDATE**, r = 0.610).
Consumed by G-NL's decomposition arm only.

### X4 — xG per shot (trailing) — ADOPTED
`Σ sm_xg / Σ sm_shots` over the trailing window (regulation shots
only; ratio of sums; min 8 window matches with shotmap, else NaN).
Availability: all seasons (shotmap 100%). Justification: F6
(**SIGNAL-CANDIDATE**, r = 0.759 — stronger than J1's 0.437).
Consumed by S-NL's quality-input arm.

### X5 — Trailing target-rate means (naive / ensemble components) — ADOPTED
Trailing-10 team means of the candidate's own target (SOT, corners,
unified yellows, total shots) and the conceded means — the naive
component of the reference architectures and the harness's naive
baseline. Window: trailing 10 team matches, strictly pre-match;
fewer than 6 of 10 carrying the stat → NaN. Availability: **all
seasons for all four targets** (no dead windows, unlike J2/J3).
Justification: F2 (target traits reliable: SOT-for 0.924,
corners-for 0.849, yellows-for 0.502, shots-for 0.927).

### X6 — Attacking xGOT per shot (trailing, era-guarded) — ADOPTED
`Σ sm_xgot / Σ sm_xgot_n` over the trailing window, counting **only
matches from the 2024/2025 season onward** (before that the field
is populated only for on-target shots — a different quantity).
Min 8 era-valid window matches, else NaN (arm inactive). This
makes the feature unavailable for predictions before ~mid-2024/2025
by construction. Attacking side only. Justification: F7
(**SIGNAL-CANDIDATE**, era-restricted r = 0.522). Consumed by
S-NL's recent-era arm only.

### X7 — Opp-box touches for / against (trailing) — ADOPTED (with gaps)
Trailing means of stats-feed `touches_opp_box` for/against; min 8
window matches with the stat, else NaN (arm inactive for that
team-match). Availability: 69–85% of matches 2021/2022–2023/2024,
100% from 2024/2025 — the min-8 rule absorbs the gaps exactly as it
did for J1 2021. Justification: F9 (**SIGNAL-CANDIDATE**: for
r = 0.959, against r = 0.876, on present matches). Consumed by
C-NL's territorial-multiplier arm.

### X8 — Referee yellow rate (trailing) — ADOPTED
The appointed referee's trailing mean of unified yellows per match
within this league, shrunk toward the league mean with the
shrinkage weight fixed in the prereg; referees with fewer than 8
prior in-league matches take the shrunk league mean. Referee
identity: `content.matchFacts.infoBox.Referee.text` (coverage
**100%** in the warehouse). Leakage guard: only the referee's
matches strictly before kickoff count; the identity itself is a
fixture fact. Operational condition (from the design): if the
appointment is not published pre-match in the live pipeline, the
fixture falls back to the base arm. Justification: F8
(**SIGNAL-CANDIDATE**, r = 0.512). Consumed by K-NL's referee arm.

### X9 — Reference territorial covariates (corners Gate Zero arm) — ADOPTED
Trailing means of stats-feed `BallPossesion` and `big_chance`
for/against — production `model_corners_v3`'s multiplier
covariates, carried unchanged so Gate Zero is the true production
pattern. Justification: production adoption evidence + F9
(possession-for r = 0.944, big-chance-for r = 0.912 on this corpus).

## §2 Architectural components — explicitly NOT features

Same boundary as J1: ratings, home advantage, Dixon-Coles rho and
NB sizes are fitted parameters of the reference architectures, not
covariates. v5's Beta-Binomial on-target ratio is a fitted latent
component of the S-NL reference architecture (its presence in Gate
Zero is what S-NL's harder-shrinkage arm tests — F6). **League
half-share constants** (goals 0.444, SOT 0.446, corners 0.462,
total shots 0.449, yellows 0.333 — F3) are frozen constants for
report-style splits, presentation only, never features. League
base rates / naive baselines belong to the evaluation harness.

## §3 REJECTED features

| # | Feature | Verdict / reason |
|---|---|---|
| R1 | Team first-half shares (all markets) | **NOISE** — F3: true variance ≤ 0 (goals/SOT/shots) or small-positive with team r ≈ 0 (corners/yellows). The halves book stays closed. |
| R2 | Trailing finishing (goals − xG) as a covariate | **NOT CONSUMED** — measured r = 0.407 in this league (F6), recorded honestly; but the DC blend (X1) fits on goals directly, so team finishing is already inside the goals ratings. Adding it again would double-count. Eligible only under a new design that removes the goals half of the blend — not this program. |
| R3 | Trailing conversion (goals / shot) as a covariate | **REJECTED** — outcome-contaminated (prices in the same finishing luck as R2); dominated by X4 + shot volume. (Not separately reliability-measured here; the J1 rejection reasoning applies a fortiori given R2's status.) |
| R4 | Standalone trailing on-target rate (SOT / shots) | **NOT CONSUMED as a covariate** — measured r = 0.581 in this league (F6), but v5's internal BB ratio component (§2) already carries this information inside the reference architecture; a second, standalone copy would double-count. The RS arm tests the component's shrinkage, which is the legitimate question. |
| R5 | Defensive xGOT per shot | **REJECTED** — not measured as a trait in this league's EDA and NOISE in J1 (r = 0.116); no evidence base. X6 is attacking-only. |
| R6 | Lineup / absence features | **CLOSED** — F10: program-wide closure stands; no reopening evidence sought or found. |
| R7 | Top-shooter concentration share as a team trait | **NO EVIDENCE** — never reliability-tested as a trait here. Ineligible. |
| R8 | Formation / coach features | **NO EVIDENCE** — present in the payload but no reliability check was run; ineligible. |
| R9 | Standings position, h2h, teamForm snapshots | **LEAKAGE** — post-match snapshots of the target match itself. |
| R10 | Attendance | **LEAKAGE / NOT PRE-MATCH** — the payload's figure is the actual crowd. |
| R11 | First-goal and other game-state traits | **NOT PRE-MATCH** — descriptive in-match facts only. |
| R12 | Red-card rates (as target or covariate) | **REJECTED** — 0.15 per match is a rare-event count; the production cards design excludes reds as a target as well. |
| R13 | Momentum | **NOT PRE-MATCH** — an in-match/live quantity in this payload. |

## §4 Consumption map (design ← features)

| Candidate | Base inputs | Variant-arm features |
|---|---|---|
| G-NL (goals) | X1 (blend), X2 | X3 (set-play decomposition arm, on top of X2) |
| S-NL (SOT) | X5 (SOT naive + ratings observations) | RS ratio-shrinkage (§2); X4 (quality input); X6 (xGOT, era arm) |
| C-NL (corners) | X5 (corners naive), X9 (Gate Zero multiplier) | X7 (box-touch multiplier arm) |
| K-NL (cards) | X5 (yellows naive + ratings) | X8 (referee arm) |
| T-NL (total shots) | X5 (shots naive + ratings observations) | v2 level layer; E9 trailing-r (family arms, as in T-J1) |
