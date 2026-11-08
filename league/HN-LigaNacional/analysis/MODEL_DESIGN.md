# Step 6 — Model design: Honduras Liga Nacional (FotMob 337)

Design authority for the preregistration. Features per
`analysis/FEATURES.md`; only G-HN reaches design — S/C/K/T are
not buildable (see §1).

## 1. Feasibility matrix

| candidate | target exists? | virgin window has target? | verdict |
|---|---|---|---|
| G-HN (goals) | yes — scores on 1,132 finished matches (1,024 regular-phase) | yes — 220 eligible regular-phase matches in 2025/2026 (Apertura + Clausura) | **BUILD** |
| S-HN (SOT) | no — `ShotsOnTarget` in 0/1,132 payloads | no | **NOT BUILDABLE** |
| C-HN (corners) | no — `corners` in 0/1,132 payloads | no | **NOT BUILDABLE** |
| K-HN (cards) | no — no stats yellows; events carry dismissals only (365 Red/YellowRed, 0 plain Yellows); referee text empty in 1,132/1,132 | no | **NOT BUILDABLE** |
| T-HN (total shots) | no — no stats, no shotmap in 0/1,132 payloads | no | **NOT BUILDABLE** |

The not-buildable verdicts are payload-level facts, not
sample-size judgements: the targets do not exist in the warehouse
for this league in any tournament. No virgin read follows for
S/C/K/T.

## 2. G-HN — goals

### Reference pattern (Gate Zero)

Production Dixon-Coles from `model_v2.py` (class `DC`), copied as
`league/HN-LigaNacional/engine/goals/dc.py`, unmodified except
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
- Fit scope: all eligible regular-phase matches dated strictly
  before the target tournament's first match date (expanding,
  tournament-blocked walk-forward: one fit per target tournament,
  whole tournament predicted from that fit).
- Teams unseen in training start at the league mean (a = d = 0).
- Teams are keyed by **FotMob team id** (`header.teams[].id`).

Sibling analogues: `league/GT-LigaNacional/prereg/PREREG_G_GT.md`
(same scores-only shape; failed its dev gate on OU2.5 LL),
`league/SV-PrimeraDivision/analysis/MODEL_DESIGN.md` (same
split-season regular-phase-only shape),
`league/GH-PremierLeague/prereg/PREREG_G_GH.md` and
`league/NG-ProfessionalLeague/prereg/PREREG_G_NG.md` (same
scores-only shape; failed their dev gates). The same gate is
applied here without modification. The counter-reading for HN:
unlike Guatemala, the attack trait is very reliable here (EDA §2:
goals-for r = 0.84), so the DC ratings have signal to work with
— the gate, not optimism, decides.

### Format rule (frozen)

FotMob 337 is a parent id; each Apertura/Clausura is a separate
sub-league id under it. The fit is pooled over the regular phase
of all tournaments; **playoff matches are excluded from every fit
and score** (PREPROCESSING.md stage rule — SV precedent for
split-season leagues: two-legged knockout ties, semifinal groups
and finals are different football from the round robin). The
2025/2026 semifinal-group matches reuse round labels 1–6 and are
separated by the date rule; they are playoff rows, excluded.
Eligible = `stage == "regular"` in `data/hn_matches.csv`
(n = 1,024).

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
   Nothing else changes. Motivation (not a measured offset): one
   new club enters at each expansion (CD Choloma 2025/26, 12th
   club 2026/27) and no cross-league mover prior exists
   (FEATURES X2), so the only sanctioned thin-data treatment is
   shrinkage. No hard-coded tier offset is used.

### Dev protocol

- Training seed = 2021/2022 - Apertura + Clausura
  (n = 180 eligible regular); evaluation tournaments 2022/2023 -
  Apertura (n = 90), 2022/2023 - Clausura (n = 90), 2023/2024 -
  Apertura (n = 90), 2023/2024 - Clausura (n = 90), 2024/2025 -
  Apertura (n = 90), 2024/2025 - Clausura (n = 90); pooled scored
  **n = 540** under the tournament-blocked expanding walk-forward.
- Metrics per arm per tournament and pooled: mean 1X2 LL, mean RPS
  (H, D, A), mean OU2.5 LL. Baselines: climatology — for target
  tournament S, pooled outcome rates + OU2.5 over-rate of all
  eligible regular-phase matches dated strictly before S's first
  match date; plus the naive trailing-10 baseline reported
  alongside (same definition as the program harness).
- Primary line OU 2.5 (ladder 1.5 / 2.5 / 3.5 reported).
- The dev harness must not read tournament "2025/2026 - Apertura",
  "2025/2026 - Clausura" or "2026/2027 - Apertura" rows at all.
  Virgin data is touched only by the separate virgin step, once,
  after dev results are frozen in the results file.

### Virgin protocol

- Virgin window: tournaments "2025/2026 - Apertura" and
  "2025/2026 - Clausura" (**n = 220, complete**). Fit = all
  eligible regular-phase matches dated before the first 2025/2026
  Apertura match (tournaments 2021/2022 - Apertura through
  2024/2025 - Clausura). Read ONCE, after dev freezes.
- Virgin climatology: pooled 2021/2022 - Apertura through
  2024/2025 - Clausura outcome rates and OU2.5 over-rate.
- Calibration per arm: (i) mean predicted home-win probability
  minus actual home-win rate; (ii) mean predicted P(over 2.5)
  minus actual over-rate. Standard error of each difference:
  SE = sd(pred_i − y_i) / √n over the 220 matches, reported with
  the difference. Calibration is defined as **actual − predicted**
  everywhere in this build (sign convention frozen here, matching
  GH/RU2/NG/SV).
- Confirmatory window "2026/2027 - Apertura" (in progress, 84
  matches to 2026-11-09) is **reserved**; it is evaluated once
  when the tournament completes and is not part of this build.

### Gate legs (verbatim, frozen — as GH/RU2/J1/NG/SV)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat
climatology, and OU2.5 LL must beat the base-rate baseline, else
the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤
Gate Zero's AND ≤ climatology's; (ii) calibration leg:
|actual − mean predicted| ≤ 1.0pp pooled for home-win rate and
for OU2.5 over-rate, SEs reported; a breach within 1 SE of the
boundary is recorded PROVISIONAL PASS, beyond it FAIL;
(iii) per-tournament sign check on dev (arm LL ≤ Gate Zero LL in
at least half the dev tournaments) for the both-pass rule.
Both-pass rule: if Gate Zero and a variant both pass all legs,
the lower pooled virgin 1X2 LL ships; if only one passes, it
ships; if none passes, G-HN verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such)
AND, for variant arms, leg (iii); Gate Zero is exempt from (iii).
Ties go to the simpler arm (Gate Zero before SHRINK). If Gate Zero
fails its own dev gate, variants are moot, verdict FAIL, virgin
NOT read.

### Halves presentation

FT + 1H/2H via the frozen goals constant 0.4572 (EDA §3):
1H λ = 0.4572 × FT λ, 2H λ = 0.5428 × FT λ; 1H OU lines 0.5/1.5/2.5,
2H OU lines 1.5/2.5/3.5, same rho and score-matrix machinery.
Halves are presentation only, never fitted.

### Outputs

Engine `league/HN-LigaNacional/engine/goals/`; dev results
`results_dev.json` (+ CSV); virgin `results_virgin.json`; fitted
params `fitted_params_virgin.json`; on PASS, virgin predictions
`league/HN-LigaNacional/predictions/g_hn_virgin_predictions.csv`
(shipped arm; FT + 1H/2H presentation via the frozen goals
constant 0.4572). Verdict:
`league/HN-LigaNacional/reports/G_HN_VERDICT.md`. Production code
untouched. No push. No merge.
