# Step 3.5 — Features: LU-NationalDivision

Consumption rule (program-wide): `MODEL_DESIGN.md` may use only the
features defined here in §1, plus the architectural components in
§2. Everything in §3 is rejected and may not re-enter through a
later phase. The J1 template features are X1–X9
(`league/J1/analysis/FEATURES.md`); each is recorded ADOPTED or
DROPPED below with its LU reason (data absent, or the reliability
check run in THIS league failed — with the number).

## §1 Accepted features

### X1 — Blend observation pair (goals-model training input)
- **ADOPTED as goals-only.** Per past match, the Dixon-Coles fit
  observes goals only. The xG half of the blend is absent: no
  `expected_goals*` key exists in any of the 1,296 payloads
  (`content.stats` is null everywhere), so every match enters under
  the reference blend's documented goals-only fallback. This is the
  same adoption as G-J2/G-J3 and G-SE.
- Justification: EDA F2 (team GF/GA traits reliable, split-half
  r=0.730/0.673 dev era) + the production blend's own gate history.

### X5 — Trailing target-rate means (naive baseline only)
- **ADOPTED for the harness baseline only.** The naive trailing-10
  baseline uses each team's trailing-10 mean goals scored as
  independent-Poisson lambdas (frozen in the prereg). No SOT /
  corners / yellows trailing means exist — the stats feed is absent
  — so X5 has no model-arm consumption in this league.
- Justification: the baseline definition in the prereg; EDA F2.

## §2 Architectural components — explicitly NOT features

- **Ratings, home advantage, Dixon-Coles rho, NB sizes** are fitted
  parameters of the shared architecture, estimated by the fit under
  the signed-age rule — not covariates.
- **League half-share constant** (LU goals 0.4294, EDA F3) is a
  frozen constant for report-style FT→1H/2H splits. It is not a
  feature, carries no team dimension, and may not be "improved"
  into a per-team or per-match quantity.
- **League base rates / naive baselines** belong to the evaluation
  harness, not to any model.
- **SHRINK** (the sanctioned G-J2-lesson variant: at prediction
  time, a team with n < 6 prior in-league matches has its attack
  and defence exponents scaled by n/6) is an architectural variant
  of the reference fit, defined verbatim from `PREREG_G_FI.md` via
  `PREREG_G_SE.md`. It is pre-registered in PREREG_G_LU.md; EDA F4
  records that it is expected to be numerically identical to Gate
  Zero in this league (no team with 1–5 prior matches in any scored
  season's training data) — the dev run confirms or refutes that.

## §3 REJECTED / DROPPED features (J1 template X1–X9)

| # | Feature | Verdict / reason |
|---|---|---|
| X1 (xG half) | Blend observation pair, xG half | **DROPPED — data absent.** No xG in any of 1,296 payloads. Goals-only fallback adopted instead (§1). |
| X2 | Mover tier offset | **DROPPED — data absent.** No sibling Luxembourg league in the warehouse (only id 229 exists for Luxembourg); no in-warehouse prior-tier history for any LU club, so no mover tilt can be estimated. Entrants (2/2/3/4 per season, EDA F4) arrive from the Division of Honour, which is not in the warehouse. No ENTRANT arm. |
| X3 | Set-play xG share/rate | **DROPPED — data absent.** Needs xG splits; none exist. |
| X4 | xG per shot (trailing) | **DROPPED — data absent.** Needs shotmap; shots empty in all 1,296 payloads. |
| X5 (SOT/corners/yellows) | Trailing target-rate means for stats markets | **DROPPED — data absent.** No SOT/corners/yellows in any season; X5 survives only as the goals naive baseline (§1). |
| X6 | Attacking xGOT per shot | **DROPPED — data absent.** Needs shotmap xGOT; none exists. |
| X7 | Opp-box touches | **DROPPED — data absent.** Needs stats feed; absent everywhere. |
| X8 | Referee yellow rate | **DROPPED — data absent (twice over).** Referee identity: `infoBox.Referee.text` is `""` in all 1,296 payloads (key present, content empty). Yellow counts: none exist (no stats feed; events carry Red/YellowRed only). Strictness is unmeasurable. |
| X9 | Reference territorial covariates (possession, big chances) | **DROPPED — data absent.** Needs stats feed; absent everywhere. No corners candidate exists to consume them. |

## §3b Rejected (J1 §3 analogues, LU readings)

| # | Feature | Verdict / reason |
|---|---|---|
| R1 | Team first-half shares (goals) | **NOISE** — EDA F3: per-season 1H shares sit within ~1 SE of the frozen 0.4294; no per-team trait evidence. Halves book stays closed. |
| R2/R3/R4 | Trailing finishing / conversion / on-target rate | **NO EVIDENCE + data absent** — no xG/shot data to compute them from. Ineligible. |
| R5 | Defensive xGOT per shot | **DROPPED — data absent.** |
| R6 | Lineup / absence features | **CLOSED + data absent** — no lineups in any payload (`content.lineup` absent 1,296/1,296); the J1 V10 verdict (no effect) also stands. |
| R7 | Top-shooter concentration | **NO EVIDENCE + data absent** — no shot/player data. |
| R8 | Formation / coach | **NO EVIDENCE + data absent** — no lineups. |
| R9 | Standings position, h2h, teamForm | **LEAKAGE** — `content.table`/`h2h`/`teamForm` are post-match snapshots of the target match itself. |
| R10 | Attendance | **LEAKAGE / NOT PRE-MATCH + data absent** — null in all payloads. |
| R11 | First-goal / game-state traits | **NOT PRE-MATCH** — descriptive in-match facts only. |
| R12 | Red-card rates (as target or covariate) | **REJECTED** — 0.30/match rare-event count; no reliability evidence; the production cards design excludes reds as a target. Red counts are descriptive CSV columns only. |
| R13 | Momentum | **NOT PRE-MATCH** — an in-match/live quantity in this payload. |

## §4 Consumption map (design ← features)

| Candidate | Base inputs | Variant-arm features |
|---|---|---|
| G-LU | X1 (goals-only) | SHRINK (§2 architectural variant; X2 rejected) |
| S-LU | — | NOT BUILDABLE (no SOT data) |
| C-LU | — | NOT BUILDABLE (no corners data) |
| K-LU | — | NOT BUILDABLE (no yellows; X8 dropped) |
| T-LU | — | NOT BUILDABLE (no shots data) |
