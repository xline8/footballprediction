# Pre-registration — G-WAL (Wales Cymru Premier goals model)

Frozen: 2026-11-10, before any fitting. Branch `build/wal-cymru-premier`.
Design authority: `league/WAL-CymruPremier/analysis/MODEL_DESIGN.md`
(G-WAL); features per `analysis/FEATURES.md` (X1 ADOPTED as goals-only
— no xG exists in this league at all, so the observation is goals-only;
X2 DROPPED — no Welsh sibling/parent league supplies a mover prior;
SHRINK is the thin-data arm, no hard-coded tier offset). Reference:
production Dixon-Coles in `model_v2.py` (class `DC`), hl = 270; sibling
analogues: `league/TZ-PremierLeague/prereg/PREREG_G_TZ.md` (same
scores-only shape; failed its dev gate on the OU2.5 leg),
`league/GH-PremierLeague/prereg/PREREG_G_GH.md`,
`league/DK-2Division/prereg/PREREG_G_DK2.md` (split-group precedent:
rounds 1–22 regular, rounds 23–32 split groups as ordinary rows with a
phase flag).

Format rule (frozen, MODEL_DESIGN): the fit pools regular-season rounds
1–22 with Championship/Relegation split-group rounds 23–32 as ordinary
rows (stage flag only, no group/stage feature anywhere). The 16 European
play-off matches (ECL Playoff 2021/22–2023/24, CL Playoff 2024/25–
2025/26) are EXCLUDED from every fit and score: knockout ties whose
stored score is not always a 90-minute score — match `3873043` (2021/2022
ECL Playoff final, Caernarfon–Flint Town United) is 0-0 at 90' with all
three goals at minutes 99, 105, 120, so its stored 2-1 is an
after-extra-time score. Teams are keyed by FotMob team id (stable across
the renames TNS/The New Saints 7852, Pontypridd Town/United 321094,
Cardiff Met University/FC 560953 — keying by name would split clubs).
Eligibility rule (frozen): eligible = stage != playoff (the `eligible`
column of `data/wal_matches.csv`; n = 1,087).
Calibration is defined as **actual − predicted** everywhere in this build.

## Reference architecture (all arms share unless an arm says otherwise)

- Dixon-Coles fit, copied pattern from production `model_v2.py`:
  iterative multiplicative updates, 14 sweeps, damping 0.7, +0.25
  smoothing, home advantage fitted (init 0.28), attack/defence per team
  (init 0), score matrix MAXG = 10, production `tau` correction.
- Rho per fit from grid (0.0, −0.05, −0.10, −0.15) by weighted
  log-likelihood on goals only, as production.
- Observation: goals only. (X1 fallback — no xG in any payload.)
- Time decay w = 0.5 ** ((cutoff − match_date).days / 270) — frozen,
  no search.
- Fit scope for target season S: all eligible matches dated strictly before
  the first match date of S (expanding, season-blocked: one fit per target
  season, whole season predicted from that fit).
- Teams unseen in training start at the league mean (a = d = 0).

## Arms

1. **Gate Zero** — the unmodified reference above.
2. **Arm SHRINK** (sanctioned G-J2-lesson arm) — Gate Zero plus
   exactly one change at prediction time: for a team with fewer than 6
   prior in-league matches in the training window, its fitted attack and
   defence ratings are shrunk toward the league mean: `a *= n/6`,
   `d *= n/6` where n = its prior in-league match count (n = 0 ⇒ a = d = 0,
   identical to Gate Zero's unseen rule; the arm bites exactly for teams
   with 1–5 prior matches). Motivation: 1–2 promoted clubs enter every
   season (EDA §5) and no cross-league mover prior exists (FEATURES X2).
   **The band does NOT occur in this league**: the static band check in
   `eda_numbers.json` finds zero teams with 1–5 prior in-league matches
   (by team id) in any dev or virgin fold — every incoming club has n = 0
   (Airbus UK Broughton, Pontypridd United, Colwyn Bay, Briton Ferry
   Llansawel, Llanelli in dev/virgin; the five 2026/27 newcomers are
   confirmatory-only). SHRINK is therefore a verified structural no-op
   here, included as the sanctioned thin-data arm and reported as such:
   the harness must report `changed_rows = 0` per fold, and SHRINK's dev
   numbers must equal Gate Zero's exactly. Nothing else changes; no
   hard-coded tier offset is used.

## Dev protocol

- Training seed = 2021/2022 (n = 192 eligible); evaluation seasons
  2022/2023 (n = 192), 2023/2024 (n = 192), and 2024/2025 (n = 192);
  pooled scored **n = 576** under the season-blocked expanding walk-forward.
- Metrics per arm per season and pooled: mean 1X2 LL, mean RPS (H, D, A),
  mean OU2.5 LL. Baselines: climatology — for target season S, pooled
  outcome rates + OU2.5 over-rate of all eligible matches dated strictly
  before S's first match date; plus the naive trailing-10 baseline reported
  alongside.
- Primary line OU 2.5 (ladder 1.5 / 2.5 / 3.5 reported).
- The dev harness must not read season "2025/2026" or "2026/2027" rows at
  all. Virgin data is touched only by the separate virgin step, once, after
  dev results are frozen in the results file.

## Virgin protocol

- Virgin window: season "2025/2026" (**n = 192, complete**). Fit = all
  eligible matches dated before the first 2025/2026 match (seasons
  2021/2022–2024/2025). Read ONCE, after dev freezes.
- Virgin climatology: pooled 2021/2022–2024/2025 outcome rates and OU2.5
  over-rate.
- Calibration per arm: (i) mean predicted home-win probability minus actual
  home-win rate; (ii) mean predicted P(over 2.5) minus actual over-rate.
  Standard error of each difference: SE = sd(pred_i − y_i) / √n over the
  192 matches, reported with the difference. (Sign convention: actual −
  predicted, as frozen above.)
- Confirmatory window "2026/2027" (in progress, 127 matches to 2026-11-06,
  under the NEW 16-team format with a three-way split) is reserved;
  evaluated once when the season completes, not part of this build.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS must beat climatology, and OU2.5 LL
must beat the base-rate baseline, else the arm is dead.
Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤
climatology's; (ii) calibration leg: |actual − mean predicted| ≤ 1.0pp
pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach
within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL;
(iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half
the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a
variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one
passes, it ships; if none passes, G-WAL verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND passes
virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such) AND, for variant
arms, leg (iii); Gate Zero is exempt from (iii). Ties go to the simpler arm
(Gate Zero before SHRINK). If Gate Zero fails its own dev gate, variants are
moot, verdict FAIL, virgin NOT read.

## Outputs

Engine `league/WAL-CymruPremier/engine/goals/`; dev results
`results_dev.json` (+ CSV, force-added); virgin results
`results_virgin.json`; fitted params `fitted_params_virgin.json`; on PASS,
virgin predictions `league/WAL-CymruPremier/predictions/g_wal_virgin_predictions.csv`
(shipped arm; 1H/2H presentation via frozen goals constant 0.4444).
Verdict: `league/WAL-CymruPremier/reports/G_WAL_VERDICT.md`.
Production code untouched. No push. No merge.
