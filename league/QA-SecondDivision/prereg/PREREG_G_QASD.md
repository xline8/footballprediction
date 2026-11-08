# Pre-registration — G-QASD (QA-SecondDivision goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/qa-seconddiv`.
Design authority: `league/QA-SecondDivision/analysis/MODEL_DESIGN.md`
(G-QASD); features per `analysis/FEATURES.md` (X1 goals-only — no xG
exists in any payload; X2 frozen QA-QatarStars priors; X3/X4/X6/X7/X8
dropped). Evidence: `analysis/EDA.md` (F1/F2/F3/F4/F5/F7). Reference:
production Dixon-Coles in `model_v2.py`; programme analogue
`league/QA-QatarStars/prereg/PREREG_G_QA.md` with the architecture carried
over verbatim (ratings fitted by direct Poisson log-likelihood maximisation,
scipy L-BFGS, sum-to-zero identification, ridge 1e-3; rho grid (0.0, −0.05,
−0.10, −0.15) by training log-likelihood; MAXG = 10; tau = standard
Dixon-Coles low-score correction; home init 0.25). No time decay (frozen:
the corpus spans 20 months and the dev window is a single season — decay
would be an untestable extra parameter). The ONLY reference divergence: the
observation is goals-only in every match (the X1 blend's documented
fallback), because the QA-SecondDivision feed carries no xG in any season.
Calibration is defined as **actual − predicted** everywhere in this build.

## Arms
1. **Gate Zero** — the reference above, unmodified. A team with no fitted
   rating (absent from the training window) is predicted at league mean
   (attack/defence exponents 0.0).
2. **ENTRANT** — Gate Zero plus: at prediction time, a team in its entrant
   season (played no match in the immediately preceding season) has its
   attack exponent shifted by −0.2391 and its defence exponent shifted by
   −0.1947 (both frozen, from the QA-QatarStars warehouse: EDA F4 of
   PREREG_G_QA — dev entrant offsets GF −0.3561 / GA +0.3598 against the
   QA dev scored mean team goals 1.6742/match; attack factor
   (1.6742 − 0.3561)/1.6742 = 0.7873, log −0.2391; defence factor
   (1.6742 + 0.3598)/1.6742 = 1.2149, log +0.1947, applied as a reduction
   of the defence exponent because a worse defence raises the opponent's
   expected goals). No within-league mover history exists before the virgin
   (2024/2025 is the first warehouse season), so the offset is a frozen
   warehouse prior, not a within-league estimate — recorded here, not
   adjusted for. The offset applies to the team's fitted rating if it has
   one from an earlier season (returning team), otherwise to the league-mean
   fallback (0.0).
   The SHRINK arm (G-J2 lesson) is NOT built: its failure mode (extreme
   lambdas for 1–2-match teams in season openers) cannot occur in this
   build's dev or virgin (see MODEL_DESIGN.md).

## Baselines (both, frozen)
- **Climatology / league base rate**: for each scored date, pooled outcome
  rates (H/D/A) and OU2.5 over-rate of all league matches strictly before
  that date (expanding), as constant probabilities for every scored match.
- **Naive trailing-10**: for each match, independent Poissons with means
  equal to each team's mean goals scored in its last 10 league matches
  strictly before the match (fewer if fewer exist; if none, the training
  league mean team goals/match). 1X2 and OU2.5 probabilities from the
  resulting 11×11 score matrix (MAXG = 10). No home advantage, no ratings,
  no fitted parameter beyond the training league mean fallback.

## Dev protocol
Within-season walk-forward over 2024/2025 (n = 56): warm-up = rounds 1–7
(28 matches, never scored); scored = rounds 8–14 (**28 matches**),
predicted date-grouped with an expanding fit on all league matches
strictly before each scored date. Metrics per arm, pooled over the scored
block: mean 1X2 LL, mean RPS (H, D, A), mean OU2.5 LL. The dev harness must
not read 2025/2026 or 2026/2027 rows at all. Small-n note, stated before
fitting: at n = 28 the dev LL comparisons are noisy; the gate is applied
mechanically regardless.

## Virgin protocol
Virgin = 2025/2026 (n = 56, complete season), read ONCE, only for
dev-passing arms. Fit expands to all matches of 2024/2025. Climatology =
pooled 2024/2025 rates. Calibration: actual − mean predicted for home-win
rate and OU2.5 over-rate, SE = sd(y_i − p_i)/√n.
2026/2027 is the reserved confirmatory window for goals — NOT read in this
build.

## GATE LEGS (verbatim, frozen)
Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology AND
naive trailing-10, and OU2.5 LL must beat both baselines, else the arm is
dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤
climatology's; (ii) calibration leg: |actual − mean predicted| ≤ 1.0pp
pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach
within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL;
(iii) variant sign check: pooled dev 1X2 LL ≤ Gate Zero's pooled dev 1X2
LL. Both-pass rule: if Gate Zero and ENTRANT both pass all legs, the lower
pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes,
G-QASD verdict is FAIL and nothing ships.
Mechanical reading: an arm passes iff it survives the dev gate AND passes
virgin legs (i)–(ii) (PROVISIONAL counts) AND, for variants, leg (iii);
Gate Zero is exempt from (iii). Ties → simpler arm (Gate Zero, ENTRANT).
If Gate Zero fails its dev gate, ENTRANT is moot, verdict FAIL, virgin NOT
read. Note (recorded before fitting): ENTRANT is dev-identical to Gate Zero
(no entrants in the 2024/2025 dev season), so leg (iii) is vacuous for it
and the virgin decides between the arms on the entrant's matches alone.

## Outputs
Engine `engine/goals/`; `results_dev.json` (+ CSV); `results_virgin.json`;
`fitted_params_virgin.json`; on PASS, `predictions/g_qasd_virgin_predictions.csv`
(1H/2H presentation via frozen goals constant 0.4589). Verdict `reports/G_QASD_VERDICT.md`.
