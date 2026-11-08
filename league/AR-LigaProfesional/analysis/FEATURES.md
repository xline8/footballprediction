# Phase 3.5 — Data Processing / Feature Engineering (AR-LigaProfesional)

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
Availability: **2023 onward, 100%**; 2021–2022 have no xG base
(28 shotmap matches aside, which do not constitute a feed), so the
blend's goals-only fallback carries those blocks — the J1 pattern
(J1's 2021 was the same). Justification: F11 (goals/xG 0.90–0.94
per xG-era block) + F1/F2.

### X2 — Mover / newcomer tier offset (prior for promoted clubs) — ADOPTED
For a club whose previous completed block was outside this league
(it appears in block S but not S−1), its rating prior at block
entry is shifted by the F4 offset magnitudes measured on this
corpus: attack **−0.12** goals/match, defence **+0.18**
goals/match (pooled over the five transitions with movers; the
offset is applied as a log-ratio shift against the decayed league
team mean, exactly as in G-J1's X2 arm). The offset used for block
S is the pooled historical magnitude — a design constant frozen
in the prereg, not re-estimated on S. Availability: 2 newcomers
at each year boundary (2022, 2023, 2024, 2025 - Apertura,
2026 - Apertura); none at Apertura→Clausura transitions.
Justification: F4 (**SIGNAL, weak-moderate** — recorded honestly;
the arm is gated, Gate Zero is the fallback).

### X3 — Set-play xG share and rate (trailing) — ADOPTED
`sp_share = Σ expected_goals_set_play / Σ expected_goals`,
`sp_rate = Σ expected_goals_set_play / matches` over the trailing
window (ratio of sums; min 8 window matches with xG, else NaN).
Availability: 2023 onward (xG splits are in the stats feed from
2023). Justification: F5 (**SIGNAL-CANDIDATE, modest**, r = 0.353).
Consumed by G-AR's decomposition arm only.

### X4 — xG per shot (trailing) — ADOPTED
`Σ sm_xg / Σ sm_shots` over the trailing window (regulation shots
only; ratio of sums; min 8 window matches with shotmap, else NaN).
Availability: 2023 onward (shotmap 100% from 2023; the 28
shotmap matches of 2021–2022 cannot fill a window and never
activate the feature). Justification: F6 (**SIGNAL-CANDIDATE**,
r = 0.472). Consumed by S-AR's quality-input arm.

### X5 — Trailing target-rate means (naive / ensemble components) — ADOPTED
Trailing-10 team means of the candidate's own target (SOT, corners,
unified event yellows, total shots) and the conceded means — the
naive component of the reference architectures and the harness's
naive baseline. Window: trailing 10 team matches, strictly
pre-match; fewer than 6 of 10 carrying the stat → NaN.
Availability: **all blocks for all four targets** (every target
exists for every match in this corpus). Justification: F2 (target
traits reliable: SOT-for 0.763, corners-for 0.622, yellows-for
0.564, shots-for 0.747).

### X6 — Attacking xGOT per shot (trailing, era-guarded) — ADOPTED
`Σ sm_xgot / Σ sm_xgot_n` over the trailing window, counting **only
matches dated 2025-01-01 or later** (before that the field is
populated only for on-target shots, or partially in 2024 — a
different quantity). Min 8 era-valid window matches, else NaN (arm
inactive). This makes the feature unavailable for predictions
before ~mid-2025 - Apertura by construction. Attacking side only.
Justification: F7 (**SIGNAL-CANDIDATE**, era-restricted
r = 0.422). Consumed by S-AR's recent-era arm only.

### X7 — Opp-box touches for / against (trailing) — ADOPTED (with gaps)
Trailing means of stats-feed `touches_opp_box` for/against; min 8
window matches with the stat, else NaN (arm inactive for that
team-match). Availability: 44–63% of matches 2021–2023, 100% from
2024 — the min-8 rule absorbs the gaps exactly as it did for J1
2021. Justification: F9 (**SIGNAL-CANDIDATE**: for r = 0.749,
against r = 0.802, on present matches). Consumed by C-AR's
territorial-multiplier arm.

### X8 — Referee yellow rate (trailing) — ADOPTED
The appointed referee's trailing mean of unified (event) yellows
per match within this league, shrunk toward the league mean with
the shrinkage weight fixed in the prereg; referees with fewer than
8 prior in-league matches take the shrunk league mean. Referee
identity: `content.matchFacts.infoBox.Referee.text` (coverage
**0% in 2021** — the field is empty — ~100% from 2022, **100% in
the virgin block**). Leakage guard: only the referee's matches
strictly before kickoff count; the identity itself is a fixture
fact. Operational condition (from the design): if the appointment
is not published pre-match in the live pipeline, the fixture falls
back to the base arm. Justification: F8 (**SIGNAL-CANDIDATE**,
r = 0.724 — the program's strongest referee trait so far).
Consumed by K-AR's referee arm.

### X9 — Reference territorial covariates (corners Gate Zero arm) — ADOPTED
Trailing means of stats-feed `BallPossesion` and `big_chance`
for/against — production `model_corners_v3`'s multiplier
covariates, carried unchanged so Gate Zero is the true production
pattern. Justification: production adoption evidence + F9
(possession-for r = 0.940, big-chance-for r = 0.641 on this
corpus).

## §2 Architectural components — explicitly NOT features

Same boundary as J1: ratings, home advantage, Dixon-Coles rho and
NB sizes are fitted parameters of the reference architectures, not
covariates. v5's Beta-Binomial on-target ratio is a fitted latent
component of the S-AR reference architecture (its presence in Gate
Zero is what S-AR's harder-shrinkage arm tests — F6). **League
half-share constants** (goals 0.444, SOT 0.459, corners 0.480,
total shots 0.462, yellows 0.373 — F3) are frozen constants for
report-style splits, presentation only, never features. League
base rates / naive baselines belong to the evaluation harness.

## §3 REJECTED features

| # | Feature | Verdict / reason |
|---|---|---|
| R1 | Team first-half shares (all markets) | **NOISE** — F3: true variance ≤ 0 (goals) or small-positive with team r ≈ 0 or negative (SOT/corners/shots/yellows). The halves book stays closed. |
| R2 | Trailing finishing (goals − xG) as a covariate | **REJECTED** — measured r = 0.138 in this league (near-noise, F6); and the DC blend (X1) fits on goals directly, so team finishing is already inside the goals ratings. Adding it again would double-count. |
| R3 | Trailing conversion (goals / shot) as a covariate | **REJECTED** — outcome-contaminated (prices in the same finishing luck as R2); dominated by X4 + shot volume. (Not separately reliability-measured here; the J1 rejection reasoning applies a fortiori given R2's status.) |
| R4 | Standalone trailing on-target rate (SOT / shots) | **NOT CONSUMED as a covariate** — measured r = 0.555 in this league (F6), but v5's internal BB ratio component (§2) already carries this information inside the reference architecture; a second, standalone copy would double-count. The RS arm tests the component's shrinkage, which is the legitimate question. |
| R5 | Defensive xGOT per shot | **REJECTED** — not measured as a trait in this league's EDA and NOISE in J1 (r = 0.116); no evidence base. X6 is attacking-only. |
| R6 | Lineup / absence features | **CLOSED** — F10: program-wide closure stands; no reopening evidence sought or found. |
| R7 | Top-shooter concentration share as a team trait | **NO EVIDENCE** — never reliability-tested as a trait here. Ineligible. |
| R8 | Formation / coach features | **NO EVIDENCE** — present in the payload but no reliability check was run; ineligible. |
| R9 | Standings position, h2h, teamForm snapshots | **LEAKAGE** — post-match snapshots of the target match itself. (Zone standings in the split era are additionally a mid-bracket artefact.) |
| R10 | Attendance | **LEAKAGE / NOT PRE-MATCH** — the payload's figure is the actual crowd. |
| R11 | First-goal and other game-state traits | **NOT PRE-MATCH** — descriptive in-match facts only. |
| R12 | Red-card rates (as target or covariate) | **REJECTED** — 0.27 per match is a rare-event count; the production cards design excludes reds as a target as well. |
| R13 | Momentum | **NOT PRE-MATCH** — an in-match/live quantity in this payload. |

## §4 Consumption map (design ← features)

| Candidate | Base inputs | Variant-arm features |
|---|---|---|
| G-AR (goals) | X1 (blend, goals-only fallback 2021–2022), X2 | X3 (set-play decomposition arm, on top of X2) |
| S-AR (SOT) | X5 (SOT naive + ratings observations) | RS ratio-shrinkage (§2); X4 (quality input); X6 (xGOT, era arm) |
| C-AR (corners) | X5 (corners naive), X9 (Gate Zero multiplier) | X7 (box-touch multiplier arm) |
| K-AR (cards) | X5 (yellows naive + ratings) | X8 (referee arm) |
| T-AR (total shots) | X5 (shots naive + ratings observations) | v2 level layer; E9 trailing-r (family arms, as in T-J1) |
