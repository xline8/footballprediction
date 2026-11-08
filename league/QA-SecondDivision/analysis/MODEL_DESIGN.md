# Step 6 — Model Design: QA-SecondDivision

Design authority for the preregistrations in `prereg/`. Features per
`analysis/FEATURES.md`; evidence per `analysis/EDA.md` (F1–F7). All five
candidates are buildable (unlike the parent league, where S/C/K/T had no
dev window at all): the stats era starts mid-2024/2025, so a within-season
dev scored block exists for every market. The corpus is thin everywhere
(F7) — every verdict must carry the small-n caveat.

## Feasibility matrix

| Candidate | Target exists | Dev scored window | Virgin window | Buildable |
|---|---|---|---|---|
| G-QASD goals | yes, all seasons | 2024/2025 R8–14 (n=28) | 2025/2026 complete (56) | YES |
| S-QASD SOT | yes, stats era | 2025/2026 R8–14 (n=28) | 2026/2027 partial (29, TRANSITIONAL) | YES |
| C-QASD corners | yes, stats era | 2025/2026 R8–14 (n=28) | 2026/2027 partial (29, TRANSITIONAL) | YES |
| K-QASD yellows | yes, events all seasons | 2025/2026 R8–14 (n=28) | 2026/2027 partial (29, TRANSITIONAL) | YES |
| T-QASD total shots | yes, stats era | 2025/2026 R8–14 (n=28) | 2026/2027 partial (29, TRANSITIONAL) | YES |

## Windows (frozen)

- **G**: warm-up 2024/2025 rounds 1–7 (28 matches, never scored); scored
  2024/2025 rounds 8–14 (28), expanding fit on all league matches strictly
  before each scored date, date-grouped. Virgin 2025/2026 complete (56),
  read ONCE, only for dev-passing arms; fit expands to all 2024/2025.
  2026/2027 is the reserved confirmatory window — NOT read in this build.
  Rationale for the SA-style split (rather than warm-up 2024/2025, dev
  2025/2026, virgin 2026/2027 partial): the virgin that matters for
  calibration should be a *complete* season (n=56, SE ≈6.5pp) rather than
  a 29-match partial (SE ≈9pp); the dev scored block is thin either way
  (28 vs 56) and the dev gate is mechanical on whichever block is frozen.
- **S/C/T/K**: warm-up 2025/2026 rounds 1–7 (28 matches, never scored);
  scored 2025/2026 rounds 8–14 (28), expanding fit on all league matches
  with the target strictly before each scored date (fit history therefore
  includes the 2024/2025 stats-era rounds 6–14, 38 matches), date-grouped.
  Virgin 2026/2027 partial (29, rounds 1–6, TRANSITIONAL), read ONCE, only
  for dev-passing arms, continuing from the dev end state; confirmatory
  re-read at season end.
- **Alternative considered and rejected for S/C/T/K**: a pooled dev scored
  block of 2024/2025 stats-era rounds 10–14 (20) + 2025/2026 rounds 8–14
  (28) = 48. Rejected: the 2024/2025 block's trailing windows reach into
  the stat-less rounds 1–5 (degraded to NaN by the X5 minimum rule), and a
  20-match partial-season block adds more complexity than evidence. The
  SA-mirror split (dev within one full-stats season) is cleaner and is
  frozen here.
- **Calibration definition**: actual − predicted everywhere in this build
  (mean P(over) − actual rate for S/C/T/K; home-win rate and OU2.5
  over-rate for G), SE = sd(p_i − y_i)/√n. Gate: |breach| ≤ 1.0pp clean
  PASS; breach within 1 SE of the boundary = PROVISIONAL PASS; else FAIL.

## G-QASD (goals)

- **Reference**: production Dixon-Coles in `model_v2.py`, programme analogue
  `league/QA-QatarStars/prereg/PREREG_G_QA.md` (architecture carried over
  verbatim): ratings by direct Poisson log-likelihood maximisation, scipy
  L-BFGS, sum-to-zero identification, ridge 1e-3; rho grid (0.0, −0.05,
  −0.10, −0.15) by training log-likelihood; MAXG = 10; tau = standard
  Dixon-Coles low-score correction; home init 0.25. No time decay (frozen:
  the corpus spans 20 months and the dev window is a single season — decay
  would be an untestable extra parameter). The ONLY divergence: the
  observation is goals-only in every match (X1 fallback — no xG exists).
  A team with no fitted rating (absent from the training window) is
  predicted at league mean (attack/defence exponents 0.0).
- **Arms**: (1) **Gate Zero** — the reference above, unmodified.
  (2) **ENTRANT** — Gate Zero plus, at prediction time, for a team in its
  entrant season (played no match in the immediately preceding season):
  attack exponent −0.2391, defence exponent −0.1947 (frozen QA-QatarStars
  warehouse priors, FEATURES.md X2; defence exponent is reduced because
  a worse defence raises the opponent's expected goals). The offset
  applies to the team's fitted rating if it has one from an earlier season
  (returning team), otherwise to the league-mean fallback (0.0).
- **SHRINK not built** (G-J2 lesson considered): the failure mode it
  addresses — extreme lambdas for 1–2-match teams in season openers —
  cannot occur in this build's dev or virgin. Dev warm-up gives every team
  7 matches before scoring starts; the virgin fit uses the full 2024/2025
  (14 matches per team) and the sole entrant (Al-Khor) is unseen, so Gate
  Zero already assigns it league-mean ratings. SHRINK would be dev-identical
  to Gate Zero and is not a distinguishable arm here. Recorded, not built.
- **Known risk (recorded, not patched)**: the single-home-intercept DC
  underfit away goals in QA-QatarStars (near-zero home advantage; F1 shows
  the same pattern here — 2025/2026 away teams outscore home teams). The
  dev gate arbitrates; no intercept is added post-hoc.
- **Primary line**: OU2.5 (dev over-rate 0.446, closest to 0.5; F5).
- **Halves**: FT + 1H/2H presentation-only via frozen goals constant 0.4589.
- **Dev gate** (QA wording): pooled dev 1X2 LL and RPS of an arm must beat
  climatology AND naive trailing-10, and OU2.5 LL must beat both baselines,
  else the arm is dead. **Virgin legs**: (i) LL: arm's virgin 1X2 LL ≤ Gate
  Zero's AND ≤ climatology's; (ii) calibration: |mean predicted − actual|
  ≤ 1.0pp pooled for home-win rate and OU2.5 over-rate, SEs reported,
  breach within 1 SE = PROVISIONAL PASS; (iii) variant sign check: pooled
  dev 1X2 LL ≤ Gate Zero's pooled dev 1X2 LL. Both-pass rule: if Gate Zero
  and ENTRANT both pass all legs, the lower pooled virgin 1X2 LL ships; if
  only one passes, it ships; if none passes, G-QASD verdict is FAIL and
  nothing ships. Ties → simpler arm (Gate Zero). If Gate Zero fails its dev
  gate, ENTRANT is moot, verdict FAIL, virgin NOT read. Note: ENTRANT is
  dev-identical to Gate Zero (no entrants in the 2024/2025 dev season), so
  leg (iii) is vacuous for it and the virgin decides between the arms on
  the entrant's matches alone — recorded here before fitting.

## S-QASD (shots on target)

- **Reference**: production `model_sot.py` v5; SA analogue
  `league/SA-FirstDivision/prereg/PREREG_S_SAFD.md` — the v5 architecture
  constants are carried over verbatim (ridge lambda = 100, HL = 365, lazy
  refit 7 days, total-shots ratings prior K = 8, Beta-Binomial prior
  P = 200, ensemble 50/50 with naive trailing-10, NB size r = 79.94
  frozen). Engine port: `league/SCO-Premiership/engine/sot/`.
- **Target**: total SOT = `ShotsOnTarget_home + ShotsOnTarget_away`
  (stats feed). **Primary line 8.5** (dev over-rate 0.482; F5).
  Ladder 7.5 / 8.5 / 9.5 reported, gate at 8.5.
- **Arms**: **Gate Zero** (v5 unmodified); **RS** (Gate Zero with the BB
  prior raised P = 200 → 20,000). X4/X6 are NOT arms: no shotmap and no
  xGOT exist in any era (FEATURES.md).
- **Baselines**: league base rate (over-8.5 rate of all matches strictly
  before each scored date, expanding); naive trailing-10 through the same NB.
- **Dev gate**: pooled dev LL@8.5 beats BOTH baselines, else arm dead, no
  virgin read. **Virgin legs**: (i) LL@8.5 ≤ Gate Zero's and ≤ best
  baseline's; (ii) calibration |mean P(over 8.5) − actual| ≤ 1.0pp, SE
  reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev sign check
  (variant pooled dev LL@8.5 ≤ Gate Zero's). Both-pass: both → lower pooled
  virgin LL ships; one → ships; none → FAIL. Ties → Gate Zero.
- **Outputs**: `engine/sot/`; `results_dev.json` (+ CSV);
  `results_virgin.json`; `fitted_params_virgin.json`; on PASS,
  `predictions/s_qasd_virgin_predictions.csv` (FT ladder 7.5/8.5/9.5;
  1H/2H presentation-only via frozen SOT constant 0.4194).

## C-QASD (corners)

- **Reference**: production `model_corners_v3.py`; SA analogue
  `league/SA-FirstDivision/prereg/PREREG_C_SAFD.md` — shared engine carried
  over verbatim in form (HL = 270 base rates, rolling-5 relative factors
  clamped [0.6, 1.7], core mean `mu_cs`, NB pmf grid 0..50, gamma grid
  (0.0, 0.15, 0.3, 0.45, 0.6, 0.8), r clamped [1.02, 5.0], territorial
  multiplier clamped [0.70, 1.43], min-8 of last-10 validity rule,
  date-grouped predict-then-update state). Engine port:
  `league/SCO-Premiership/engine/corners/`.
- **Target**: total corners (stats feed). **Primary line 9.5** (dev over-rate
  0.464; F5). Ladder 8.5 / 9.5 / 10.5 reported, gate at 9.5.
- **Arms**: **Gate Zero (X9)** — production covariates `BallPossesion` +
  `big_chance`, beta grids exactly as PREREG_C_J1 (poss ∈ ±{0, .0025, .005,
  .0075, .010}, bc ∈ ±{0, .025, .05, .075, .10}). **No X7 arm**: X7 is
  dropped — `touches_opp_box` does not exist in this feed (FEATURES.md).
  The `big_chance` covariate is degenerate (0/0 in every match) and is
  carried as a zero column so Gate Zero stays the unmodified production
  pattern; the engine records this rather than silently dropping it.
- **Baselines**: league base rate (NB from the decay-weighted expanding
  history before each scored date, as PREREG_C_J1) and naive trailing-10
  (X5) through the same per-date NB size.
- **Dev gate / virgin legs / both-pass**: as S-QASD, at line 9.5.
- **Outputs**: `engine/corners/`; `results_dev.json` (+ CSV);
  `results_virgin.json`; `fitted_params_virgin.json`; on PASS,
  `predictions/c_qasd_virgin_predictions.csv` (FT ladder 8.5/9.5/10.5;
  1H/2H presentation-only via frozen corners constant 0.4495).

## K-QASD (cards)

- **Reference**: production `model_cards.py`; SA analogue
  `league/SA-FirstDivision/prereg/PREREG_K_SAFD.md` and its engine — the
  architecture (team yellow ratings + count distribution + naive ensemble
  structure of the reference) is carried over in form. Engine port:
  `league/SCO-Premiership/engine/cards/`.
- **Target**: unified yellows = `yellow_home + yellow_away` — the **event
  feed** (Yellow + YellowRed), `cards_source='events'` for every match.
  The stats feed was rejected as the target source on dev-era evidence
  measured before fitting (stats undercounts events one-directionally:
  2025/2026 dev season 37 exact / 19 low / 0 high, mean −0.52; pooled
  pre-virgin 71 / 23 / 0, mean −0.40), following the AR/BR/NO/SA precedent.
  **Primary line 5.5** (dev over-rate 0.500, exactly — closest to 0.5; F5).
  Ladder 4.5 / 5.5 / 6.5 reported, gate at 5.5.
- **Arms**: **Gate Zero only** (reference unmodified; referee not used).
  The X8 referee arm is NOT built: referee coverage is 0% in both dev
  seasons (EDA F6). Team yellow trait reliability is noise here (F2:
  r = −0.01 odd/even / −0.28 chrono) — recorded, not patched; the gate
  decides.
- **Baselines**: league base rate (over-5.5 rate of all matches strictly
  before each scored date, expanding); naive trailing-10 through the same
  count distribution as the reference harness.
- **Dev gate / virgin legs / both-pass**: as S-QASD, at line 5.5 (Gate Zero
  only, so leg (iii) is vacuous; Gate Zero dev failure ⇒ FAIL, virgin NOT
  read).
- **Outputs**: `engine/cards/`; `results_dev.json` (+ CSV);
  `results_virgin.json`; `fitted_params_virgin.json`; on PASS,
  `predictions/k_qasd_virgin_predictions.csv` (FT ladder 4.5/5.5/6.5;
  1H/2H presentation-only via frozen yellows constant 0.3151).

## T-QASD (total shots)

- **Reference**: the shots family as frozen for T-J1 (v1 pattern / v2 level
  layer / E9 trailing-r) — see `league/J1/prereg/PREREG_T_J1.md` for the
  three arms' exact constructions and mirror them, changing only league,
  seasons and line. SA analogue `PREREG_T_SA.md`. Engine port:
  `league/SCO-Premiership/engine/total_shots/`.
- **Target**: total shots = `total_shots_home + total_shots_away` (stats
  feed). **Primary line 23.5** (dev over-rate 0.446; F5). Ladder
  22.5 / 23.5 / 24.5 reported, gate at 23.5.
- **Arms**: **A** v1 pattern (ratings + NB + naive ensemble); **B** v2
  pattern (+ level layer); **C** E9 (NB r from a trailing window,
  league-level analogue). The port's internal tuning-block mechanics use
  the warm-up block (first 28 matches of 2025/2026, never scored) exactly
  as the SCO port used its first scored season; the gate pool is the scored
  block below.
- **Baselines**: league base rate (over-23.5 rate of all matches strictly
  before each scored date, expanding); naive trailing-10.
- **Dev gate / virgin legs / both-pass**: as S-QASD, at line 23.5, with leg
  (i) reading LL@23.5 ≤ the reference arm's (arm A if it passes dev;
  otherwise the dev-passing arm with the lowest pooled dev LL) and ≤ best
  baseline's. Variant sign check: pooled dev LL@23.5 ≤ reference arm's
  pooled dev LL@23.5; ties → simpler arm A before B before C.
- **Outputs**: `engine/total_shots/`; `results_dev.json` (+ CSV);
  `results_virgin.json`; `fitted_params_virgin.json`; on PASS,
  `predictions/t_qasd_virgin_predictions.csv` (FT ladder 22.5/23.5/24.5;
  1H/2H presentation-only via frozen shots constant 0.4456).
- **Trial separation**: T-QASD is a separate corpus from the top-5
  prospective total-shots trial (v2 vs E9); neither contaminates the other.

## Verdicts

One verdict per candidate: `reports/<X>_QASD_VERDICT.md` with dev + virgin
tables vs baselines (league base rate at the primary line; naive
trailing-10), the exact gate arithmetic, and what ships (nothing on FAIL;
the winning arm + its fitted params on PASS). Predictions CSV (virgin
window, winning arm) under `league/QA-SecondDivision/predictions/` on PASS,
force-added. A FAIL is a complete, respectable outcome; report it as
plainly as a PASS.
