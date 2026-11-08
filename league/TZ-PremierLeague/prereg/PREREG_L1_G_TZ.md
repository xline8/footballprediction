# Pre-registration — Lane 1 re-entry G-TZ-L1 (Tanzania Premier League goals)

Frozen: 2026-11-11, before any sealed-season access under this entry.
Branch `build/lane1-gtz`. This file is the branch's FIRST commit; its
commit message states that it precedes any sealed access, and no sealed
data may be loaded before that commit exists.

Authority: `league/IMPROVEMENT_PROGRAM.md` (Lane 1 — unread sealed
windows) and `league/improvement_scratch/LANE1_WAVE1/cohort_report.md`
§1.2 / §1.5 / §3 row 9 (G-TZ, cohort A — variants-moot). Original
candidate: `league/TZ-PremierLeague/prereg/PREREG_G_TZ.md`; original
verdict: `league/TZ-PremierLeague/reports/G_TZ_VERDICT.md` (FAIL at the
dev gate; virgin deliberately NOT read).

## 1. The method difference (stated in advance, the only one)

- **Arm of record = SHRINK.** The SHRINK arm of the original prereg —
  Gate Zero plus exactly one prediction-time change: for a team with
  fewer than 6 prior in-league matches in the training window, its
  fitted attack and defence ratings are shrunk toward the league mean,
  `a *= n/6`, `d *= n/6`, where n is its prior in-league match count
  (n = 0 is the unseen-team rule, identical to Gate Zero) — is the arm
  judged by this entry. Its definition is unchanged, character for
  character, from the original prereg.
- **Gate Zero is retained as a baseline only.** Its dev numbers are
  recomputed and reported, and it is the reference for the dev sign
  check (leg iii), but its dev pass is NO LONGER a precondition for the
  arm of record's sealed read. That precondition is the
  gate-architecture defect this Lane 1 entry exists to correct: in the
  original build Gate Zero failed one of three pooled dev legs
  (OU2.5 LL 0.716160 vs base rate 0.692720) and the frozen
  "variants are moot" rule therefore blocked SHRINK, which had passed
  all three pooled dev legs on its own numbers (1X2 LL 0.925501,
  RPS 0.180158, OU2.5 LL 0.689404). Removing the veto is the stated
  method difference; nothing else about the gates changes.
- **Leg (i) reference substitution (pinned verbatim, per cohort
  report §1.5 for G-TZ).** Because Gate Zero is a baseline only, no
  Gate Zero sealed LL is produced as a gate reference. Sealed leg (i)
  is therefore read against climatology and the baselines: the arm of
  record's sealed 1X2 LL must be ≤ climatology's sealed 1X2 LL. (The
  original leg (i) additionally required ≤ Gate Zero's sealed LL;
  that comparison cannot exist once Gate Zero's dev veto is removed,
  and this substitution is the coordinator-pinned reading for G-TZ.)

## 2. Reference architecture (unchanged from the original prereg)

- Dixon-Coles fit, copied pattern from production `model_v2.py`:
  iterative multiplicative updates, 14 sweeps, damping 0.7, +0.25
  smoothing, home advantage fitted (init 0.28), attack/defence per
  team (init 0), score matrix MAXG = 10, production `tau` correction.
- Rho per fit from grid (0.0, −0.05, −0.10, −0.15) by weighted
  log-likelihood on goals only, as production.
- Observation: goals only (no xG exists in this league).
- Time decay w = 0.5 ** ((cutoff − match_date).days / 270) — frozen.
- Fit scope for target season S: all eligible matches dated strictly
  before the first match date of S (expanding, season-blocked: one
  fit per target season, whole season predicted from that fit).
- Teams unseen in training start at the league mean (a = d = 0).
- Format rule (frozen): FotMob 9066 is a single-table league; the fit
  is pooled over the single table. The two awarded matches are
  EXCLUDED from every fit and score: `3726033` (2021/2022, 3-0) and
  `4950929` (2025/2026, 0-3). Teams are keyed by name. Eligibility:
  eligible = not awarded (the `eligible` column of
  `data/tz_matches.csv`).
- Presentation halves share (goals, 1H): 0.4867818118 — presentation
  only; no gate leg consumes it.

## 3. Dev protocol (via `league/gate_lib/`)

- Training seed = 2021/2022 (n = 239 eligible); evaluation seasons
  2022/2023 (n = 240), 2023/2024 (n = 240), 2024/2025 (n = 240);
  pooled scored **n = 720** under the season-blocked expanding
  walk-forward, recomputed with the league engine on dev data only.
- The dev evaluation MUST reproduce the documented dev pass of the
  arm of record on all three legs, within artefact rounding, against
  the numbers persisted in the original build's
  `engine/goals/results_dev.json` and quoted in §1 above (SHRINK
  pooled 1X2 LL 0.925501, RPS 0.180158, OU2.5 LL 0.689404;
  climatology pooled 1X2 LL 1.069080, RPS 0.223944, OU base rate
  0.692720). If it does NOT reproduce, the entry STOPS: no sealed
  read, and the verdict is written as a STOPPED report explaining
  the discrepancy.
- Baselines: climatology — for target season S, pooled outcome rates
  + OU2.5 over-rate of all eligible matches dated strictly before
  S's first match date; plus the naive trailing-10 baseline reported
  alongside. The OU2.5 dev leg is read against the base rate
  (climatology OU2.5 LL), exactly as in the original prereg.
- The dev harness must not read season "2025/2026" or "2026/2027"
  rows at all (enforced with `league/gate_lib/`'s
  `assert_no_sealed_rows` on the dev load).
- On a reproduced dev pass, the dev-pass token for candidate
  `G-TZ-L1` is recorded in the gate_lib registry
  (`league/gate_lib.record_dev_pass`) BEFORE any sealed load; the
  sealed window is then loaded ONCE through the fail-closed sealed
  loader (`league/gate_lib.load_sealed_rows`).

## 4. Sealed (virgin) protocol — one read, verdict final

- Virgin window: season "2025/2026" (**n = 239, complete**), the
  original virgin season named in the original prereg
  (`virgin_primary: 2025/2026` in `league/TZ-PremierLeague/config.yaml`).
  Fit = all eligible matches dated before the first 2025/2026 match
  (seasons 2021/2022–2024/2025).
- Virgin climatology: pooled 2021/2022–2024/2025 outcome rates and
  OU2.5 over-rate.
- Calibration sign convention: **predicted − actual** (the
  `league/gate_lib/` convention, P5). This supersedes the original
  prereg's actual − predicted wording for REPORTING; every
  calibration leg below is an absolute value, so no leg's outcome
  depends on the sign choice. Calibration is reported for
  (i) home-win probability and (ii) P(over 2.5), each as mean
  predicted − actual in percentage points, with
  SE = sd(pred_i − y_i) / √n over the 239 matches.
- Confirmatory window "2026/2027" is NOT part of this entry and is
  not read.
- One read of the named sealed window. No iteration against the
  window after the read. The verdict is final.

## 5. GATE LEGS (identical to the original goals prereg, §1 aside)

Primary line OU 2.5 (ladder 1.5 / 2.5 / 3.5 reported).

Dev gate — the arm of record's pooled dev 1X2 LL and RPS must beat
climatology, and its pooled dev OU2.5 LL must beat the base rate
baseline, else the arm is dead and the sealed window is not read.

Sealed legs —

- (i) LL leg: the arm of record's sealed 1X2 LL ≤ climatology's
  sealed 1X2 LL (reference substitution pinned in §1; the original
  leg's ≤ Gate Zero sealed comparison is the one element the Lane 1
  method difference removes).
- (ii) Calibration leg (two-part): |predicted − actual| ≤ 1.0 pp
  pooled for the home-win rate AND for the OU2.5 over-rate, SEs
  reported; a breach within 1 SE of the boundary
  (|difference| ≤ 1.0 pp + SE) on a part is recorded PROVISIONAL for
  that part, beyond it FAIL for that part. Both parts must pass
  (clean or provisional) for the leg to pass.
- (iii) Per-season sign check on dev: the arm of record's dev 1X2 LL
  ≤ Gate Zero's dev 1X2 LL in at least half the dev seasons
  (≥ 2 of the 3 dev seasons).

Both-pass semantics (original rule, degenerated to one judged arm):
Gate Zero is a baseline only and cannot ship under this entry. If
the arm of record passes the dev gate AND sealed legs (i)–(iii),
it ships; if any leg fails, G-TZ-L1 verdict is FAIL and nothing
ships. Verdict labels: CLEAN PASS when every calibration part is
within 1.0 pp; PROVISIONAL PASS when no leg fails and at least one
calibration part is provisional (breach within 1 SE of the
boundary); FAIL otherwise.

## 6. Design seal (P2) and worst-fold reporting (P6)

- EDA/design artefacts under the P2 design seal: this entry
  introduces NO new EDA and NO new design choice. The design is the
  already-frozen original design (`analysis/MODEL_DESIGN.md`,
  `analysis/FEATURES.md`); every number this entry computes before
  the sealed read is computed on dev-era seasons only (seed
  2021/2022 + dev 2022/2023–2024/2025). No sealed-season aggregate
  is consulted, recomputed, or shown before the single sealed read.
- The verdict includes the P6 worst-fold block (worst dev season's
  legs beside the pooled legs, produced by
  `league/worst_fold/`; information only, no gate change).

## 7. Outputs

- Dev recomputation + sealed computation script and results under
  `league/TZ-PremierLeague/engine/goals/` (Lane 1 artefacts named
  `results_dev_l1.json` / `results_virgin_l1.json`; the original
  build's artefacts are not overwritten).
- On PASS, virgin predictions for the shipped arm (SHRINK) at
  `league/TZ-PremierLeague/predictions/g_tz_virgin_predictions.csv`
  and fitted params `fitted_params_virgin_l1.json` in the engine
  directory (1H/2H presentation via the frozen goals constant
  0.4867818118).
- Verdict: `league/TZ-PremierLeague/reports/VERDICT_L1_G_TZ.md`,
  carrying all leg numbers (dev + sealed), the P6 worst-fold block,
  and this preregistration's commit hash.
- Production code untouched. No push. No merge.
