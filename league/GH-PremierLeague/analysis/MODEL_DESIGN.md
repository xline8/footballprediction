# Step 6 — Model design: Ghana Premier League (FotMob 522)

Design authority for the preregistrations. Features per
`analysis/FEATURES.md`; only G-GH reaches design — S/C/K/T are
not buildable (see §1).

## 1. Feasibility matrix

| candidate | target exists? | virgin window has target? | verdict |
|---|---|---|---|
| G-GH (goals) | yes — scores on 1,596 eligible matches | yes — 299 eligible matches in 2025/2026 | **BUILD** |
| S-GH (SOT) | no — `ShotsOnTarget` in 0/1,619 payloads | no | **NOT BUILDABLE** |
| C-GH (corners) | no — `corners` in 0/1,619 payloads | no | **NOT BUILDABLE** |
| K-GH (cards) | no — no stats yellows; events carry dismissals only (177 Red/YellowRed, 0 plain Yellows); referee text empty in 1,619/1,619 | no | **NOT BUILDABLE** |
| T-GH (total shots) | no — no stats, no shotmap in 0/1,619 payloads | no | **NOT BUILDABLE** |

The not-buildable verdicts are payload-level facts, not sample-size
judgements: the targets do not exist in the warehouse for this league
in any season. No virgin read follows for S/C/K/T.

## 2. G-GH — goals

### Reference pattern (Gate Zero)

Production Dixon-Coles from `model_v2.py` (class `DC`), copied as
`league/GH-PremierLeague/engine/goals/dc.py`, unmodified except
the goals-only observation (X1 fallback):

- Iterative multiplicative updates, 14 sweeps, damping 0.7, +0.25
  smoothing, home advantage fitted (init 0.28), attack/defence per
  team (init 0), score matrix MAXG = 10, production `tau`
  correction.
- Rho per fit from grid (0.0, −0.05, −0.10, −0.15) by weighted
  log-likelihood on goals only, as production.
- Observation: goals only (xG absent everywhere).
- Time decay w = 0.5 ** ((cutoff − match_date).days / 270) — frozen,
  no search.
- Fit scope: all eligible matches dated strictly before the target
  season's first match date (expanding, season-blocked walk-forward:
  one fit per target season, whole season predicted from that fit).
- Teams unseen in training start at the league mean (a = d = 0).
- Teams are keyed by **name** (no team ids exist in this corpus).

Sibling analogues: `league/NG-ProfessionalLeague/prereg/PREREG_G_NG.md`
(same scores-only shape; failed its dev gate on 1X2 LL, RPS and
OU2.5 LL) and `league/RU-SecondLeague/prereg/PREREG_G_RU2.md`
(same scores-only shape; failed its dev gate on 1X2 LL and OU2.5
LL). The same gate is applied here without modification.

### Format rule (frozen)

FotMob 522 is a single-table league id (`parentLeagueId` = 522 =
the league id itself; no sub-tournaments). The fit is pooled over
the single table; no group, stage or sub-tournament feature
anywhere. The 23 awarded/forfeit matches are **excluded from every
fit and score** (PREPROCESSING.md rule 2). The round-33 2024/2025
fixture Holy Stars vs Nations FC does not exist in the warehouse
and is therefore absent from every fit and score by construction.
Eligible = the `eligible` column in `data/gh_matches.csv` (n=1,596).

### Arms

1. **Gate Zero** — the unmodified reference above.
2. **Arm SHRINK** (sanctioned G-J2-lesson arm) — Gate Zero plus
   exactly one change at prediction time: for a team with fewer
   than 6 prior in-league matches in the training window, its
   fitted attack and defence ratings are shrunk toward the league
   mean: `a *= n/6`, `d *= n/6` where n = its prior in-league match
   count (n = 0 ⇒ a = d = 0, identical to Gate Zero's unseen rule;
   the arm bites exactly for teams with 1–5 prior matches — the
   season-opener failure mode; under date-cutoff fitting that band
   may not occur, which is itself a recorded finding if so).
   Nothing else changes. Motivation (not a measured offset): 3–4
   promoted clubs enter every season (EDA §5) and no cross-league
   mover prior exists (FEATURES X2), so the only sanctioned
   thin-data treatment is shrinkage. No hard-coded tier offset is
   used.

### Dev protocol

- Training seed = 2021/2022 (n = 306 eligible); evaluation seasons
  2022/2023 (n = 306), 2023/2024 (n = 305), 2024/2025 (n = 290);
  pooled scored **n = 901** under the season-blocked expanding
  walk-forward.
- Metrics per arm per season and pooled: mean 1X2 LL, mean RPS
  (H, D, A), mean OU2.5 LL. Baselines: climatology — for target
  season S, pooled outcome rates + OU2.5 over-rate of all eligible
  matches dated strictly before S's first match date; plus the
  naive trailing-10 baseline reported alongside (same definition
  as the program harness).
- Primary line OU 2.5 (ladder 1.5 / 2.5 / 3.5 reported).
- The dev harness must not read season "2025/2026" or "2026/2027"
  rows at all. Virgin data is touched only by the separate virgin
  step, once, after dev results are frozen in the results file.

### Virgin protocol

- Virgin window: season "2025/2026" (**n = 299, complete**). Fit =
  all eligible matches dated before the first 2025/2026 match
  (seasons 2021/2022–2024/2025). Read ONCE, after dev freezes.
- Virgin climatology: pooled 2021/2022–2024/2025 outcome rates and
  OU2.5 over-rate.
- Calibration per arm: (i) mean predicted home-win probability minus
  actual home-win rate; (ii) mean predicted P(over 2.5) minus actual
  over-rate. Standard error of each difference:
  SE = sd(pred_i − y_i) / √n over the 299 matches, reported with the
  difference. Calibration is defined as **actual − predicted**
  everywhere in this build (sign convention frozen here, matching
  RU2/NG).
- Confirmatory window "2026/2027" (in progress, 90 matches to
  2026-11-08) is **reserved**; it is evaluated once when the season
  completes and is not part of this build.

### Gate legs (verbatim, frozen — as RU2/J1/NG)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat
climatology, and OU2.5 LL must beat the base-rate baseline, else the
arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate
Zero's AND ≤ climatology's; (ii) calibration leg: |actual − mean
predicted| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate,
SEs reported; a breach within 1 SE of the boundary is recorded
PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev
(arm LL ≤ Gate Zero LL in at least half the dev seasons) for the
both-pass rule. Both-pass rule: if Gate Zero and a variant both pass
all legs, the lower pooled virgin 1X2 LL ships; if only one passes,
it ships; if none passes, G-GH verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such)
AND, for variant arms, leg (iii); Gate Zero is exempt from (iii).
Ties go to the simpler arm (Gate Zero before SHRINK). If Gate Zero
fails its own dev gate, variants are moot, verdict FAIL, virgin
NOT read.

### Outputs

Engine `league/GH-PremierLeague/engine/goals/`; dev results
`results_dev.json` (+ CSV); virgin `results_virgin.json`; fitted
params `fitted_params_virgin.json`; on PASS, virgin predictions
`league/GH-PremierLeague/predictions/g_gh_virgin_predictions.csv`
(shipped arm; 1H/2H presentation via frozen goals constant 0.4622).
Verdict: `league/GH-PremierLeague/reports/G_GH_VERDICT.md`.
Production code untouched. No push. No merge.
