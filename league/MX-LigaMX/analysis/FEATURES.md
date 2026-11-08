# Phase 3.5 — Data Processing / Feature Engineering (MX-LigaMX)

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
Availability: **100% of every tournament** (unlike J1/AR there is
no xG-less era; the blend's goals-only fallback is retained as
code, it simply never binds). Justification: F11 (goals/xG
0.95–1.14 per tournament, pooled ≈1.05) + F1/F2.

### X2 — Mover / newcomer tier offset — DROPPED
There are no movers to measure: the same 18 clubs play all 10
tournaments, with zero entrants and zero departures at all 9
transitions (no promotion/relegation since 2020 — F4). A mover
offset estimated on zero movers would be fiction. Dropped, with
the G-J2 thin-team concern noted as non-binding (expanding-window
history is deep for every club after warm-up).

### X3 — Set-play xG share and rate (trailing) — ADOPTED
`sp_share = Σ expected_goals_set_play / Σ expected_goals`,
`sp_rate = Σ expected_goals_set_play / matches` over the trailing
window (ratio of sums; min 8 window matches with xG, else NaN).
Availability: all tournaments (xG splits ride with the 100% xG
feed). Justification: F5 (**SIGNAL-CANDIDATE**, r = 0.558).
Consumed by G-MX's decomposition arm only.

### X4 — xG per shot (trailing) — ADOPTED
`Σ sm_xg / Σ sm_shots` over the trailing window (regulation shots
only; ratio of sums; min 8 window matches with shotmap, else NaN).
Availability: all tournaments (shotmap 100%). Justification: F6
(**SIGNAL-CANDIDATE**, r = 0.626). Consumed by S-MX's quality arm.

### X5 — Trailing target-rate means (naive / ensemble components) — ADOPTED
Trailing-10 team means of the candidate's own target (SOT, corners,
unified event yellows, total shots) and the conceded means — the
naive component of the reference architectures and the harness's
naive baseline. Window: trailing 10 team matches, strictly
pre-match; fewer than 6 of 10 carrying the stat → NaN.
Availability: **all tournaments for all four targets**.
Justification: F2 (SOT-for 0.848, corners-for 0.670, yellows-for
0.528, shots-for 0.845).

### X6 — Attacking xGOT per shot (trailing, era-guarded) — DROPPED
The era guard would be matches dated 2025-01-01 or later (xGOT
complete only from 2024/2025 Clausura, F7), but the trait itself
fails the reliability standard in THIS league: era-restricted
split-half r = **0.073** (all-era 0.012), against J1's 0.518 and
AR's 0.422 where the arm was adopted. A feature whose trait does
not reproduce is dropped, never faked; the era guard is moot.
S-MX runs GZ / RS / X4 only.

### X7 — Opp-box touches for / against (trailing) — ADOPTED (with early gaps)
Trailing means of stats-feed `touches_opp_box` for/against; min 8
window matches with the stat, else NaN (arm inactive for that
team-match). Availability: 39–96% of matches in the first four
tournaments, 100% from 2023/2024 Apertura — the min-8 rule absorbs
the gaps. Justification: F9 (**SIGNAL-CANDIDATE**: for r = 0.863,
against r = 0.890). Consumed by C-MX's territorial arm.

### X8 — Referee yellow rate (trailing) — ADOPTED (weak trait, coverage caveat)
The appointed referee's trailing mean of unified (event) yellows
per match within this league, shrunk toward the league mean with
the shrinkage weight fixed in the prereg (K = 8 match-equivalents,
HL = 270, factor clamped to [0.8, 1.25] — the AR K prereg's frozen
form); referees with no prior in-league matches — and matches with
no named referee — get factor 1.0. Referee identity:
`content.matchFacts.infoBox.Referee.text` (coverage **0% in the
warm-up tournament**, 95–100% through 2024/2025 Clausura, **24.8%
in 2025/2026 Apertura, 58.2% in the virgin block**). Leakage
guard: only the referee's matches strictly before kickoff count.
Operational condition: if the appointment is not published
pre-match in the live pipeline, the fixture falls back to the base
arm. Justification: F8 (**SIGNAL-CANDIDATE, weak**, r = 0.331 —
the weakest referee trait among leagues that adopted X8; the arm
is gated and Gate Zero is the fallback). Consumed by K-MX only.

### X9 — Reference territorial covariates (corners Gate Zero arm) — ADOPTED
Trailing means of stats-feed `BallPossesion` and `big_chance`
for/against — production `model_corners_v3`'s multiplier
covariates, carried unchanged so Gate Zero is the true production
pattern. Justification: production adoption evidence + F9
(possession-for r = 0.927, big-chance-for r = 0.726).

## §2 Architectural components — explicitly NOT features

Same boundary as J1/AR: ratings, home advantage, Dixon-Coles rho
and NB sizes are fitted parameters of the reference architectures,
not covariates. v5's Beta-Binomial on-target ratio is a fitted
latent component of the S-MX reference architecture (its presence
in Gate Zero is what S-MX's harder-shrinkage arm RS tests — F6).
**League half-share constants** (goals 0.456, SOT 0.455, corners
0.465, total shots 0.458, yellows 0.385 — F3) are frozen constants
for report-style splits, presentation only, never features. League
base rates / naive baselines belong to the evaluation harness.

## §3 REJECTED features

| # | Feature | Verdict / reason |
|---|---|---|
| R1 | Team first-half shares (all markets) | **NOISE** — F3: true variance ≈ +0.001 (goals/SOT/corners), +0.0004 (shots), +0.0071 (yellows). The halves book stays closed. |
| R2 | Trailing finishing (goals − xG) as a covariate | **REJECTED** — r = 0.171 in this league (F6, near-noise); and the DC blend (X1) already fits on goals directly, so finishing is inside the goals ratings. Adding it again would double-count. |
| R3 | Trailing conversion (goals / shot) as a covariate | **REJECTED** — outcome-contaminated (same finishing luck as R2); dominated by X4 + shot volume. |
| R4 | Standalone trailing on-target rate (SOT / shots) | **NOT CONSUMED as a covariate** — measured r = 0.488 here (F6), but v5's internal BB ratio component (§2) already carries this information; a second standalone copy would double-count. The RS arm tests the component's shrinkage. |
| R5 | Attacking xGOT per shot (X6) | **DROPPED** — era-restricted reliability r = 0.073 (F7): NOISE in this league, unlike J1/AR. |
| R6 | Defensive xGOT per shot | **REJECTED** — NOISE in J1 (r = 0.116) and no evidence base here. |
| R7 | Altitude (home stadium elevation) as a covariate / arm | **NOT ADOPTED** — F12: large descriptive gap (+0.586 vs +0.221 home-goal edge) but altitude is a fixed attribute of six specific clubs in a league whose team set never changes; it is collinear with team identity and already absorbed by team/venue ratings. No within-team variation exists to identify it, so no reliability check can license it. |
| R8 | Lineup / absence features | **CLOSED** — F10: program-wide closure stands; no reopening evidence sought or found. |
| R9 | Top-shooter concentration share as a team trait | **NO EVIDENCE** — never reliability-tested as a trait here. Ineligible. |
| R10 | Formation / coach features | **NO EVIDENCE** — present in the payload but no reliability check was run; ineligible. |
| R11 | Standings position, h2h, teamForm snapshots | **LEAKAGE** — post-match snapshots of the target match itself. |
| R12 | Attendance | **LEAKAGE / NOT PRE-MATCH** — the payload's figure is the actual crowd. |
| R13 | First-goal and other game-state traits | **NOT PRE-MATCH** — descriptive in-match facts only. |
| R14 | Red-card rates (as target or covariate) | **REJECTED** — rare-event count; the production cards design excludes reds as a target as well. |
| R15 | Momentum | **NOT PRE-MATCH** — an in-match/live quantity in this payload. |

## §4 Consumption map (design ← features)

| Candidate | Base inputs | Variant-arm features |
|---|---|---|
| G-MX (goals) | X1 (blend; fallback never binds) | X3 (set-play decomposition arm) |
| S-MX (SOT) | X5 (SOT naive + ratings observations) | RS ratio-shrinkage (§2); X4 (quality input). **No X6 — dropped (R5).** |
| C-MX (corners) | X5 (corners naive), X9 (Gate Zero multiplier) | X7 (box-touch multiplier arm) |
| K-MX (cards) | X5 (yellows naive + ratings) | X8 (referee arm, weak trait + coverage caveat) |
| T-MX (total shots) | X5 (shots naive + ratings observations) | v2 level layer; E9 trailing-r (family arms, as in T-J1) |
