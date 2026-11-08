# Phase 3.5 — Data Processing / Feature Engineering (SE-Allsvenskan)

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
Justification: F11 (goals/xG 0.89–1.07 per season, pooled ≈ 0.99)
+ F1/F2.

### X2 — Mover / newcomer tier offset — DROPPED
Promoted sides arrive from Superettan, which is **not in this
corpus**, so no cross-tier offset is estimable (F4 — same position
as DK; contrast J1, where both tiers were in-corpus). The thin-data
problem the offset would have addressed is instead handled by the
goals candidate's pre-registered SHRINK arm (the sanctioned G-J2
lesson). No offset is faked from another league's magnitudes.

### X3 — Set-play xG share and rate (trailing) — ADOPTED
`sp_share = Σ expected_goals_set_play / Σ expected_goals`,
`sp_rate = Σ expected_goals_set_play / matches` over the trailing
window (ratio of sums; min 8 window matches with xG, else NaN).
Availability: all seasons (xG splits are in the stats feed
throughout). Justification: F5 (**SIGNAL-CANDIDATE**, r = 0.617).
Consumed by G-SE's decomposition arm only.

### X4 — xG per shot (trailing) — ADOPTED (weak evidence, arm only)
`Σ sm_xg / Σ sm_shots` over the trailing window (regulation shots
only; ratio of sums; min 8 window matches with shotmap, else NaN).
Availability: all seasons (shotmap 99.9%). Justification: F6
(**SIGNAL-CANDIDATE, weak**, r = 0.268 — the weakest X4 evidence in
the program; J1 0.437, DK 0.348). It exists only as a gated variant
arm in S-SE; the gate decides.

### X5 — Trailing target-rate means (naive / ensemble components) — ADOPTED
Trailing-10 team means of the candidate's own target (SOT, corners,
unified yellows, total shots) and the conceded means — the naive
component of the reference architectures and the harness's naive
baseline. Window: trailing 10 team matches, strictly pre-match;
fewer than 6 of 10 carrying the stat → NaN. Availability: **all
seasons for all four targets** (no dead windows, unlike J2/J3).
Justification: F2 (target traits reliable: SOT-for 0.836,
corners-for 0.757, yellows-for 0.707, shots-for 0.884).

### X6 — Attacking xGOT per shot (trailing, era-guarded) — DROPPED
Era guard for this league would be 2025 onward (xGOT populated for
~100% of shots only from 2025), but the era-guarded reliability
check **fails**: split-half r = 0.099 (F7). Dropped, never faked.
S-SE runs three arms, not four (same outcome as DK).

### X7 — Opp-box touches for / against (trailing) — ADOPTED (with gaps)
Trailing means of stats-feed `touches_opp_box` for/against; min 8
window matches with the stat, else NaN (arm inactive for that
team-match). Availability: 39–51% of matches 2021–2023, 100% from
2024 — the min-8 rule absorbs the gaps exactly as it did for J1
2021 / DK. Justification: F9 (**SIGNAL-CANDIDATE**: for r = 0.872,
against r = 0.809, on present matches). Consumed by C-SE's
territorial-multiplier arm.

### X8 — Referee yellow rate (trailing) — ADOPTED (with fallbacks)
The appointed referee's trailing mean of unified yellows per match
within this league, shrunk toward the league mean with the
shrinkage weight fixed in the prereg; referees with fewer than 8
prior in-league matches — and matches whose referee identity is
**unknown** (0% named in 2021, 12–29% unnamed from 2022) — fall
back to the base arm. No imputation. Leakage guard: only the
referee's matches strictly before kickoff count; the identity
itself is a fixture fact. Operational condition: if the appointment
is not published pre-match in the live pipeline, the fixture falls
back to the base arm. Justification: F8 (**SIGNAL-CANDIDATE**,
r = 0.616). Consumed by K-SE's referee arm.

### X9 — Reference territorial covariates (corners Gate Zero arm) — ADOPTED
Trailing means of stats-feed `BallPossesion` and `big_chance`
for/against — production `model_corners_v3`'s multiplier
covariates, carried unchanged so Gate Zero is the true production
pattern. Justification: production adoption evidence + F9
(possession-for r = 0.924, big-chance-for r = 0.786 on this corpus).

## §2 Architectural components — explicitly NOT features

Same boundary as J1: ratings, home advantage, Dixon-Coles rho and
NB sizes are fitted parameters of the reference architectures, not
covariates. v5's Beta-Binomial on-target ratio is a fitted latent
component of the S-SE reference architecture (its presence in Gate
Zero is what S-SE's harder-shrinkage arm tests — F6). **League
half-share constants** (goals 0.440, SOT 0.455, corners 0.473,
total shots 0.457, yellows 0.370 — F3) are frozen constants for
report-style splits, presentation only, never features. League
base rates / naive baselines belong to the evaluation harness.

## §3 REJECTED features

| # | Feature | Verdict / reason |
|---|---|---|
| R1 | Team first-half shares (all markets) | **NOISE** — F3: true variance ≤ 0 (goals/SOT/shots) or small-positive level-only (corners/yellows). The halves book stays closed. |
| R2 | Trailing finishing (goals − xG) as a covariate | **NOISE / NOT CONSUMED** — r = 0.272 (F6); and the DC blend (X1) already fits on goals directly, so team finishing is inside the goals ratings. |
| R3 | Trailing conversion (goals / shot) as a covariate | **REJECTED** — outcome-contaminated (prices in the same finishing luck as R2); dominated by X4 + shot volume. |
| R4 | Standalone trailing on-target rate (SOT / shots) | **NOT CONSUMED as a covariate** — r = 0.210 (weak, F6); v5's internal BB ratio component (§2) already carries this information inside the reference architecture. The RS arm tests the component's shrinkage, which is the legitimate question. |
| R5 | Defensive xGOT per shot | **REJECTED** — NOISE in J1 (r = 0.116) and the attacking side itself fails here (F7). |
| R6 | Lineup / absence features | **CLOSED** — F10: program-wide closure stands; no reopening evidence sought or found. |
| R7 | Top-shooter concentration share as a team trait | **NO EVIDENCE** — never reliability-tested as a trait here. Ineligible. |
| R8 | Formation / coach features | **NO EVIDENCE** — present in the payload but no reliability check was run; ineligible. |
| R9 | Standings position, h2h, teamForm snapshots | **LEAKAGE** — post-match snapshots of the target match itself. |
| R10 | Attendance | **LEAKAGE / NOT PRE-MATCH** — the payload's figure is the actual crowd. |
| R11 | First-goal and other game-state traits | **NOT PRE-MATCH** — descriptive in-match facts only. |
| R12 | Red-card rates (as target or covariate) | **REJECTED** — 0.10 per match is a rare-event count; the production cards design excludes reds as a target as well. |
| R13 | Momentum | **NOT PRE-MATCH** — an in-match/live quantity in this payload. |

## §4 Consumption map (design ← features)

| Candidate | Base inputs | Variant-arm features |
|---|---|---|
| G-SE (goals) | X1 (blend) | SHRINK (thin-data prior, sanctioned G-J2 lesson — replaces the inestimable X2); X3 (set-play decomposition arm, on top of SHRINK) |
| S-SE (SOT) | X5 (SOT naive + ratings observations) | RS ratio-shrinkage (§2); X4 (quality input, weak trait) |
| C-SE (corners) | X5 (corners naive), X9 (Gate Zero multiplier) | X7 (box-touch multiplier arm) |
| K-SE (cards) | X5 (yellows naive + ratings) | X8 (referee arm, with unknown-identity fallback) |
| T-SE (total shots) | X5 (shots naive + ratings observations) | v2 level layer; E9 trailing-r (family arms, as in T-J1) |
