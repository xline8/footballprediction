# Step 5 — Feature Engineering: UAE Pro League

J1 template (X1–X9) adjudicated against THIS league's data. The global
causality contract of `league/J1/analysis/FEATURES.md` §1 applies
verbatim (strictly pre-match trailing/expanding inputs, ratio-of-sums,
NaN ⇒ arm inactive, never filled from the target match).

## §1 Verdicts

| # | Feature | Verdict | Reason (this league's numbers) |
|---|---|---|---|
| X1 | Blend pair (goals, xG) | **ADOPTED, goals-only** | Goals exist 100%; xG exists in **0/959** payloads (no shotmap, no `expected_goals` key). The reference blend degrades to goals-only by its own documented fallback — not a variant. |
| X2 | Mover tier offset | **DROPPED** | The feeder tier (UAE Division 1) is not in this corpus, so no mover transitions can be estimated in-league. The sanctioned substitute is the pre-registered SHRINK arm on goals (thin-history shrinkage, G-J2 lesson), which needs no cross-tier data. |
| X3 | Set-play xG share | **DROPPED** | No xG of any kind exists. |
| X4 | xG per shot | **DROPPED** | No shotmap exists (0 shots in 959 payloads). |
| X5 | Trailing target-rate means (naive/ensemble) | **ADOPTED** | Every target (SOT, corners, stats yellows, total shots) exists in 100% of matches in every season; traits reliable per EDA F2. |
| X6 | xGOT per shot | **DROPPED** | No shotmap exists. |
| X7 | Opp-box touches for/against | **ADOPTED** | Key present 100% from 2022/2023 (134/182 in 2021/2022, min-8 rule absorbs); trait r=0.951 for / 0.864 against (EDA F2) — the strongest territorial trait measured in this program. Consumed by the corners X7 arm. |
| X8 | Referee yellow rate | **DROPPED** | Referee named in only 6/182 virgin matches (3.3%) and 25–67% of dev matches; just 9 referees reach 16 named matches (r=0.43 on that thin subset). The arm could not be validated in the virgin window (K-J1's 0.5%-coverage lesson). Cards run Gate Zero only. |
| X9 | Reference territorial covariates (possession, big chances) | **ADOPTED** | Both keys in 100% of matches; big-chance-for trait r=0.912, possession r=0.970. Carried unchanged as the corners Gate Zero multiplier, so Gate Zero is the true production pattern. |

## §2 Architectural components (not features)

Ratings, home advantage, DC rho, NB sizes, and v5's internal
Beta-Binomial on-target ratio are fitted components of the reference
architectures (J1 FEATURES §2 applies). League half-share constants
(EDA F3: goals 0.4463, SOT 0.4618, corners 0.4801, total shots 0.4608,
yellows 0.3724) are frozen presentation constants, never features.

## §3 Rejected (inherited, restated for this league)

Team first-half shares (noise), trailing finishing/conversion,
standalone trailing on-target rate as a covariate (despite r=0.64 here —
it remains outcome-contaminated and is already represented inside v5's
fitted ratio component), lineup/absence features (closed program-wide),
standings/h2h snapshots (post-match leakage), red cards as a target.

## §4 Consumption map

| Candidate | Base inputs | Variant arms |
|---|---|---|
| G-AE goals | X1 goals-only | SHRINK (thin-history shrinkage) |
| S-AE SOT | X5 | RS (harder ratio shrinkage, prior 200→20,000) |
| C-AE corners | X5, X9 (Gate Zero) | X7 (box-touch multiplier) |
| K-AE cards | X5 | — (Gate Zero only; X8 dropped) |
| T-AE total shots | X5-family ratings | A v1 / B v2 level layer / C E9 trailing-r |
