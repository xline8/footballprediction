# Step 5 — Feature Engineering: PE-Liga1

The J1 template (X1–X9) applied to this league. **Consumption rule:
`MODEL_DESIGN.md` may use only the features defined in §1, plus the
architectural components delimited in §2. Everything in §3 is
rejected — explicitly, with its reason.** The global causality
contract is J1's, unchanged: features for a target match M use only
matches with kickoff strictly before M; windows are trailing or
expanding-with-decay inside a block-blocked fit; ratio features are
ratios of sums; where a window cannot be filled the feature is NaN
and the arm that needs it is inactive for that match — never
silently filled.

## §1 Template verdicts for THIS league

### X1 — Blend observation pair — ADOPTED, reduced to goals-only
Per past match, (goals, team xG) entering the Dixon-Coles fit.
xG availability: **zero files in the entire corpus** carry an
`expected_goals` key, and there is no shotmap. The production
blend's documented goals-only fallback is therefore not a fallback
here — it is the whole design. Justification: F1/F2 (goals traits
r = 0.666 / 0.862).

### X2 — Entrant tier offset — ADOPTED (variant arm, G-PE)
For a club absent from Liga 1 in the previous calendar year, its
fitted attack/defence ratings at prediction time for its entry
year are **replaced** by frozen offsets estimated from dev-era
(2022–2024) arrivals only (F4: ΔGF −0.082, ΔGA +0.142 per match vs
league mean 1.317): `a = ln(0.9375) = −0.0645`,
`d = ln(1.1078) = +0.1024`. There is no feeder corpus in the
warehouse (Peru has no Liga 2 in the index), so the flag is
absence-based (`absent_prev`), exactly the measurable part of the
CO-A X2 construction. Leakage guard: offsets use only arrivals
completed before the virgin year; a club's own entry-year matches
never inform its offset.

### X3 — Set-play xG share/rate — DROPPED
No xG of any kind exists in this corpus. Data absent; never faked.

### X4 — xG per shot — DROPPED
No shotmap (0 files) and no xG. Data absent.

### X5 — Trailing target-rate means — ADOPTED
Trailing-10 team means of the candidate's own target (SOT, corners,
unified shots, event yellows 2023+) and the conceded means — the
naive component of the reference architectures and the harness's
naive baseline. Window: trailing 10 team matches strictly
pre-match; fewer than 6 of 10 carrying the stat → NaN.
Justification: F2 (SOT 0.598/0.536, corners 0.731/0.634, raw shots
0.643/0.610, cards-era yellows 0.518/0.354).

### X6 — Attacking xGOT per shot — DROPPED
No shotmap, no xGOT. Data absent.

### X7 — Opp-box touches for/against — ADOPTED (with coverage caveat)
Trailing means of `touches_opp_box` for/against; min-8 rule.
Justification: F9-analogue — for r = 0.666, against r = 0.614;
per-match corr with corners 0.571 vs possession 0.447. Coverage
caveat, stated plainly: rich stats are concentrated in Apertura
blocks in the dev era (every dev Clausura block has zero rich
matches), so early in each Apertura the trailing window often
cannot fill 8 rich matches and the X7 component is inactive; the
reference min-presence rules decide, nothing is imputed.
Consumed by C-PE's territorial arm only.

### X8 — Referee yellow rate — ADOPTED
The appointed referee's trailing mean of event-unified yellows per
match within this league (cards era, 2023+), in the programme's
frozen shrinkage form (K = 8 match-equivalents toward the league
mean, factor clamped to [0.8, 1.25]); unnamed/absent referee →
factor 1.0. Justification: F8 — split-half r = 0.769 on 2023–2024,
coverage 97.9% / 84.6% in the cards dev era and 80.5% in the
virgin. Operational condition (as everywhere): if the appointment
is not published pre-match in the live pipeline, the fixture falls
back to the base arm. Consumed by K-PE only.

### X9 — Reference territorial covariates (corners Gate Zero) — ADOPTED
Trailing means of `BallPossesion` (all stats rows) and `big_chance`
(rich rows) for/against — production `model_corners_v3`'s multiplier
covariates, carried unchanged so Gate Zero is the true production
pattern. Justification: production adoption + F2 (possession
r = 0.801, big chances r = 0.446).

## §2 Architectural components — explicitly NOT features

Ratings, home advantage, Dixon-Coles rho and NB sizes are fitted
parameters of the reference architectures, not covariates. v5's
Beta-Binomial on-target ratio is a fitted latent component of the
S-PE reference architecture; its harder-shrinkage arm (RS) tests
exactly that component, per the J1 §2 boundary. League half-share
constants (goals 0.4377, SOT 0.4611, corners 0.4817, total shots
0.4662, cards 0.3818) are frozen presentation constants per F3.
League base rates / naive baselines belong to the harness.

## §3 REJECTED features

| # | Feature | Verdict / reason |
|---|---|---|
| R1 | Team/match half shares (any market) | **NOISE** — F3: goals team-share split-half r = 0.151; count shares' true SD ≤ 0.08. Frozen constants only. |
| R2 | Trailing finishing / conversion (goals − xG, goals/shot) | **NO DATA / NOISE** — no xG exists; the J1 verdict (r = 0.153) stands unrebutted. |
| R3 | Standalone trailing on-target rate | **NOISE** — J1 R4 (r = 0.06); nothing here reopens it (no shotmap to re-measure with). |
| R-alt | **Altitude** (home-city elevation covariate / altitude home-advantage term) | **MEASURED, DROPPED** — F-alt: class-level home GD at ≥2,300 m is +0.555 vs +0.564 at sea level (no premium, contra the MX measurement); altitude is a fixed attribute of the home club, so the term would be collinear with team identity in this single-table league, and team ratings + the global home term already absorb the (very real) per-club home/away asymmetries. The MX discipline: measure, record, do not adopt. |
| R4 | Lineup / absence features | **CLOSED** — programme-level closure (V10 + J1 F10); no new evidence here. |
| R5 | Set-play / xG / xGOT family (X3/X4/X6 as covariates) | **NO DATA** — no xG, no shotmap in any file. |
| R6 | Red-card rates as target or covariate | **REJECTED** — rare-event count; production cards design excludes reds as a target. |
| R7 | Standings, h2h, teamForm snapshots | **LEAKAGE** — post-match snapshots of the target match itself. |
| R8 | Attendance | **NOT PRE-MATCH** — actual crowd, known only after the match (and absent here). |
| R9 | Play-off form / phase features | **OUT OF SCOPE** — play-offs are excluded from the corpus by the frozen phase rule. |
