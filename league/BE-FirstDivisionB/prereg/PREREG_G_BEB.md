# Pre-registration — G-BEB (BE-FirstDivisionB goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/be-divisionb`.
Design authority: `league/BE-FirstDivisionB/analysis/MODEL_DESIGN.md`
(G-BEB); features per `analysis/FEATURES.md` (X1 goals-only, X2
mover); evidence per `analysis/EDA.md`.
Reference: production Dixon-Coles in `model_v2.py` (class `DC`),
hl = 270; parent-tier analogue: `league/BE-FirstDivisionA/prereg/
PREREG_G_BE.md` (gate legs copied verbatim); X2 form per
`league/J1/prereg/PREREG_G_J1.md` arm 2.
Phase rule (frozen, MODEL_DESIGN): all phases (regular, promotion
group, relegation group, promotion play-off) are ordinary rows in
every fit; no phase feature anywhere.

## Era constraint (frozen)

xG does not exist anywhere in the dev era (the stats feed starts
with the virgin season). The X1 observation is therefore GOALS-ONLY
for every arm and every window of this build — the production
blend's documented fallback, applied corpus-wide, not a variant.

## Reference architecture (all arms share unless an arm says otherwise)

- Dixon-Coles fit, copied pattern from production `model_v2.py`:
  iterative multiplicative updates, 14 sweeps, damping 0.7, +0.25
  smoothing, home advantage fitted (init 0.28), attack/defence per
  team (init 0), score matrix MAXG = 10, production `tau` correction.
- Rho per fit from grid (0.0, −0.05, −0.10, −0.15) by weighted
  log-likelihood on goals only, as production.
- Observation: goals only (era constraint above).
- Time decay w = 0.5 ** ((cutoff − match_date).days / 270) — frozen.
- Fit scope for target season S: all BE-FirstDivisionB matches dated
  strictly before the first match date of S (expanding,
  season-blocked). Teams are keyed by FotMob team ID throughout.
- Teams unseen in training start at the league mean (a = d = 0).

## Arms

1. **Gate Zero** — the unmodified reference above.
2. **Arm SHRINK** (sanctioned G-J2-lesson arm) — Gate Zero plus
   exactly one change at prediction time: for a team with fewer
   than 6 prior in-league matches in the training window, its
   fitted attack and defence ratings are shrunk toward the league
   mean: `a *= n/6`, `d *= n/6` where n = its prior in-league match
   count (n = 0 ⇒ a = d = 0, identical to Gate Zero's unseen rule;
   the arm bites exactly for teams with 1–5 prior matches).
3. **Arm X2** — Arm SHRINK plus the mover prior (feature X2). A
   club is a *relegated mover* for target season S when its most
   recent prior season is the season immediately preceding S, it
   played that season in BE-FirstDivisionA (team ID present in
   `league/BE-FirstDivisionA/data/be_matches.csv` for that season),
   and it did not play BE-FirstDivisionB in that season. For a
   relegated mover, at prediction time in season S only:
   - attack: `a += log(max(mu − 0.0982, 0.10) / mu)`
   - defence: `d += log(max(mu − 0.1106, 0.10) / mu)`
   where mu is the decay-weighted mean goals per team per match in
   the training window, and −0.0982 / −0.1106 are THIS league's
   dev-era EDA magnitudes (pooled first-season-in-B goals for /
   against per match vs that season's league mean, six movers:
   Beerschot 2022/2023; Oostende, RFC Seraing, Zulte Waregem
   2023/2024; Eupen, RWD Molenbeek 2024/2025). Note the defence
   offset is negative — relegated clubs conceded LESS than the
   BE-B mean in their first season down; the arm encodes the
   measurement, not the J1 sign pattern. Reserve/U23 entrants and
   tier-3 entrants are NOT movers (no parent-tier season); they
   receive only the SHRINK/unseen treatment. A club returning to
   BE-B after a later BE-A season is a mover again for that entry
   season (the rule is evaluated per target season).

## Dev protocol

- Training seed = 2021/2022; evaluation seasons 2022/2023,
  2023/2024, 2024/2025 (pooled n = 654) under the season-blocked
  walk-forward.
- Metrics per arm per season and pooled: mean 1X2 LL, mean RPS
  (H, D, A), mean OU2.5 LL. Baselines: climatology — for target
  season S, pooled outcome rates + OU2.5 over-rate of all seasons
  strictly before S.
- The dev harness must not read 2025/2026 or 2026/2027 rows at all.

## Virgin protocol

- Virgin = 2025/2026 (n = 278, complete), read ONCE, only for arms
  passing the dev gate, after dev results are frozen and committed.
  Fit = all matches before the first 2025/2026 match date.
  Climatology = pooled 2021/2022–2024/2025 rates. Calibration:
  mean predicted − actual for home-win rate and OU2.5 over-rate,
  SE = sd(p_i − y_i)/√n.
- 2026/2027 (n = 70, partial) is confirmatory and is NOT read in
  this build under any outcome.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-BEB verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such)
AND, for variant arms, leg (iii); Gate Zero is exempt from (iii).
Ties go to the simpler arm (Gate Zero before SHRINK before X2). If
Gate Zero fails its own dev gate, variants are moot, verdict FAIL,
virgin NOT read.

## Outputs

Engine `league/BE-FirstDivisionB/engine/goals/`; dev results
`results_dev.json` (+ per-match dev predictions CSV); virgin
`results_virgin.json`; fitted params `fitted_params_virgin.json`;
on PASS, virgin predictions
`league/BE-FirstDivisionB/predictions/g_beb_virgin_predictions.csv`
(shipped arm; 1H/2H presentation via frozen goals constant
0.434014). Verdict:
`league/BE-FirstDivisionB/reports/G_BEB_VERDICT.md`.
The four not-buildable candidates get short verdict docs recording
NOT BUILDABLE with the era evidence (no fitting, no virgin read).
Production code untouched. No push. No merge.
