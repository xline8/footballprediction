# Pre-registration — G-IL (IL-LigatHaAl goals model)

Frozen: 2026-11-10, before any fitting. Design authority:
`analysis/MODEL_DESIGN.md` (G-IL); features X1 (goals-only fallback — no
xG exists in this feed: no `expected_goals*` key in any of 1,270
payloads, no shotmap), X2 entrant offset ADOPTED, X5; evidence
F1/F2/F4/F6. Reference pattern: programme Dixon-Coles (FI G analogue,
CH/EC G port). Documented port divergence: ratings fitted by direct
Poisson log-likelihood maximisation (scipy L-BFGS, sum-to-zero
identification, ridge 1e-3) instead of the production sweep optimiser;
rho selected from the grid (0.0, −0.05, −0.10, −0.15) by training
log-likelihood at the fitted ratings; MAXG = 10; tau = standard
Dixon-Coles low-score correction. All rows are ordinary rows (regular
182 + championship 30 + relegation 28 per full season; 2025/2026 is a
240-match season, used complete as-is for the virgin).

## Arms
1. **Gate Zero** — the reference above, unmodified. A team with no
   fitted rating (absent from the training seasons) is predicted at
   league mean (attack/defence exponents 0.0).
2. **ENTRANT** — Gate Zero plus: at prediction time, a team in its
   entrant season has its attack exponent shifted by −0.3143 and its
   defence exponent shifted by −0.1808 (both frozen, from EDA F4).
   The shifts are the log factors of the dev-measured entrant offsets
   against the dev scored mean team goals 1.3278/match
   (1912 goals / 720 matches / 2): attack factor
   (1.3278 − 0.3581)/1.3278 = 0.7303, log −0.3143; defence factor
   (1.3278 + 0.2631)/1.3278 = 1.1981, log +0.1808, applied as a
   reduction of the defence exponent because a worse defence raises
   the opponent's expected goals. Entrant = a team that played no
   match in the immediately preceding season (EDA F4 definition: the
   6 dev transitions are 2022/2023: 177777 Sektzia Nes Tziona,
   1121750 Maccabi Bnei Raina; 2023/2024: 7929 Maccabi Petach Tikva,
   9755 Hapoel Petah Tikva; 2024/2025: 543580 Ironi Tiberias, 2095
   Hapoel Ironi Kiryat Shmona; mean GF −0.358 / GA +0.263, GF negative
   in 5/6, GA positive in 5/6). The offset applies to the team's
   fitted rating if it has one from an earlier season (returning
   team), otherwise to the league-mean fallback (0.0).

## Baselines (both, frozen)
- **Climatology / league base rate**: pooled outcome rates (H/D/A)
  and OU2.5 over-rate over the training seasons only (prior seasons
  pooled), as constant probabilities for every scored match.
- **Naive trailing-10**: for each match, independent Poissons with
  means equal to each team's mean goals scored in its last 10 league
  matches strictly before the match (fewer if fewer exist; if none,
  the training league mean team goals/match). 1X2 and OU2.5
  probabilities from the resulting 11×11 score matrix (MAXG = 10).
  No home advantage, no ratings, no fitted parameter beyond the
  training league mean fallback.

## Dev protocol
Warm-up 2021/2022; scored seasons 2022/2023–2024/2025 (pooled n = 720),
season-blocked (expanding fit strictly before each season's first
match: train on seasons < S to score season S). Metrics: 1X2 LL,
RPS, OU2.5 LL per season and pooled, for both arms and both
baselines. The dev harness must not read 2025/2026/2026/2027 rows.

## Virgin protocol
Virgin = 2025/2026 (n = 240, complete season), read ONCE, only for
dev-passing arms. Fit expands to all matches ≤ 2024/2025. Calibration:
mean predicted − actual for home-win rate and OU2.5 over-rate,
SE = sd(p_i − y_i)/√n.

## GATE LEGS (verbatim, frozen)
Dev gate — pooled dev 1X2 LL, RPS and OU2.5 LL of an arm must beat
BOTH baselines (climatology and naive trailing-10), else the arm is
dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's
AND ≤ each baseline's, and its virgin OU2.5 LL ≤ each baseline's;
(ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for
home-win rate and for OU2.5 over-rate, SEs reported; a breach within
1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL;
(iii) per-season sign check on dev (ENTRANT 1X2 LL ≤ Gate Zero 1X2
LL in at least half the dev seasons, i.e. ≥ 2 of 3) for the
both-pass rule. Both-pass rule: if Gate Zero and ENTRANT both pass
all legs, the lower pooled virgin 1X2 LL ships; if only one passes,
it ships; if none passes, G-IL verdict is FAIL and nothing ships.
Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts) AND, for the
variant, leg (iii); Gate Zero is exempt from (iii). Ties → simpler
arm (Gate Zero before ENTRANT). If Gate Zero fails its dev gate,
variants are moot, verdict FAIL, virgin NOT read.

## Evaluation lines (frozen, EDA F6)
Primary: 1X2 and OU 2.5 (dev over-rates 1.5: 0.757, 2.5: 0.488,
3.5: 0.263; n = 720). Home win rate 0.3944, draw rate 0.2556 in the
same window. Halves presentation via the frozen goals constant
0.4497 only (config.yaml); no halves constant exists for any count
market. Predictions-only: no IL odds/settlement source in-system.

## Known calibration risk (recorded, not adjusted)
Virgin-season goals/match (2.967) sits +0.31 above the dev scored
mean (2.656), and the level was already rising within dev. A model
fitted on dev-era scoring may under-predict virgin totals; the
calibration leg (ii) will judge that as frozen. No level adjustment
is made — the gates are frozen and the virgin is read once.

## Outputs
Engine `engine/goals/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/g_il_virgin_predictions.csv` (1H/2H presentation via
frozen goals constant 0.4497). Verdict `reports/G_IL_VERDICT.md`.
