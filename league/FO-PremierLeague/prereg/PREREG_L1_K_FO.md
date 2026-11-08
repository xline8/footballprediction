# Pre-registration — L1-K-FO (FO-PremierLeague cards, Lane 1 re-entry)

**Lane 1 status.** This is a NEW candidate under the improvement
program charter (`league/IMPROVEMENT_PROGRAM.md`, Lane 1), entered
from `league/improvement_scratch/LANE1_WAVE1/cohort_report.md`
§1.2/§1.5/§3 row 2 (K-FO, cohort A — variants-moot, AUDIT.md §2
cause 4). The original candidate K-FO failed at the DEV gate
(`league/FO-PremierLeague/reports/K_FO_VERDICT.md`: FAIL, virgin
NOT read): Gate Zero scored pooled dev LL@3.5 0.6847 against the
league base rate 0.6824 and naive trailing-10 0.6930, and the
original prereg's frozen rule ("Gate Zero fails dev ⇒ variants
moot") killed the candidate before its window was read. Its sealed
window was never read and remains genuinely sealed. This
preregistration is the branch's FIRST commit, and its commit
message states that it precedes any sealed access. No sealed data
is loaded before that commit. One read, verdict final, no
iteration against the window after the read.

**Method difference, stated in advance (the sole difference).**
The arm that beat both baselines on dev — SHRINK, the shrinkage
variant — becomes the arm of record. Gate Zero is retained as a
baseline/comparator only: its dev numbers are recomputed and
reported, and it is also run on the sealed window solely as the
leg-(i) reference, but its dev pass is no longer a precondition
for the arm of record's sealed read. That precondition is the
gate-architecture defect this cohort exists to correct (cohort
report §1.5). Gate Zero's dev veto is removed as the stated method
difference. Nothing else changes: same target, same machinery,
same baselines, same gate criteria as `PREREG_K_FO.md`.

## Arm of record and comparators

- **Arm of record: SHRINK** — Gate Zero with K_PRIOR = **16**
  instead of 8 (double prior weight toward the league mean),
  exactly as frozen in `PREREG_K_FO.md` and as implemented in
  `league/FO-PremierLeague/engine/cards/` (`Online(16)` vs
  `Online(8)`). No other change. Only SHRINK can ship under this
  preregistration.
- Gate Zero — the unmodified reference architecture below — is
  retained as a comparator/baseline only. The original prereg's
  clause "Gate Zero fails dev ⇒ variants moot" does NOT apply to
  this Lane 1 candidate; that veto is the defect this re-entry
  exists to correct. SHRINK's dev gate below is judged on SHRINK's
  own numbers. Gate Zero cannot ship under this preregistration
  regardless of its numbers (see the both-pass reading below).
- Baselines (same online pass, identical match set), unchanged
  from `PREREG_K_FO.md`: league base rate and naive trailing-10.

No referee arm exists: the appointed referee's identity is empty
in all 810 payloads (`infoBox.Referee.text` == ""), so feature X8
is DROPPED at the data level and no referee covariate can be
defined. There is no referee operational gate for this candidate.

## Target and data

- Target: total yellows per match = `yellow_home + yellow_away` in
  `league/FO-PremierLeague/data/fo_premier_league_matches.csv`
  (unified yellows: Yellow + YellowRed events from the event feed;
  straight Red events are NOT counted, per program rule R12).
  The awarded match 3822183 is excluded from every pass.
- Corpus mean ≈ 3.94 yellows/match (played matches).
- Processing order is chronological by (`date`, `match_id`).
  Every prediction for a match uses only matches processed
  strictly before it in that order; state updates happen after
  prediction.

## Reference architecture (Gate Zero; all arms share it)

Copied pattern from `model_cards.py`, constants frozen at the
production values — no search:

- Exponentially decayed rates, half-life **HL = 270 days**: per
  team and venue, yellows for (attack) and yellows conceded
  (defence); decayed league means `mu_h`, `mu_a` (home/away
  yellows per match).
- Shrinkage to the league mean with prior **K_PRIOR = 8**
  match-equivalents for Gate Zero (16 for SHRINK):
  `shrunk = (s + K·mu) / (w + K)`.
- `exp_home = mu_h · (shrunk att_h(home)/mu_h) · (shrunk def_a(away)/mu_h)`;
  `exp_away` mirrored. Fallback league means before any history:
  `mu_h = 2.15`, `mu_a = 1.95`.
- Match total ~ Negative Binomial(mean = exp_home + exp_away,
  size r), `P(over L)` from the NB CDF exactly as production
  `nb_over`.

## NB size r — estimation discipline (frozen, unchanged)

Per method (Gate Zero, SHRINK, base-rate baseline, naive
baseline), r is estimated by the production experiment's method
of moments on **causal one-step-ahead residuals of earlier data
only**:

    r = Σ μ² / Σ ((y − μ)² − μ),  clipped to [2, 500];
    denominator ≤ 0 → r = 500.

- Dev scoring: r per method is estimated from season **2021**
  (warm-up) causal predictions only, then frozen for the scored
  dev seasons 2022–2025.
- Virgin scoring: r per method is re-estimated from causal
  predictions over seasons **2021–2025** only, then frozen for
  season "2026". No virgin outcome enters any r.

## Frozen line and ladder

- **Primary line: 3.5** — Ladder: 1.5 / 2.5 / 3.5 / 4.5
  (FT ladder reported; gate criteria judged at 3.5 only, secondary
  line 4.5 reported as context, exactly as in the original
  prereg).
- Log loss is the binary log loss (natural log) on P(over line).

## Dev protocol

- The dev evaluation runs through `league/gate_lib/`: the prereg
  tokens are parsed mechanically (`parse_prereg`), dev loading
  asserts no sealed rows (`assert_no_sealed_rows` against the
  sealed season 2026), and all leg arithmetic (log loss,
  calibration, sign check, calibration band) uses the gate_lib
  implementations — gate_lib numbers are the verdict's. P2 design
  seal applies to every artefact produced: EDA/design artefacts
  are computed on dev-era seasons only; this entry introduces NO
  new EDA and NO new design choice.
- Dev period: seasons 2021–2025, one chronological online
  walk-forward pass (expanding; state updates after each match).
  Season 2021 is warm-up: processed, used for the r estimation
  above, never scored. Scored dev seasons: 2022, 2023, 2024, 2025
  (pooled n = 539).
- Documented dev numbers to reproduce (from `K_FO_VERDICT.md`
  and the cohort report §1.2): SHRINK pooled dev LL@3.5
  **0.6810**, Gate Zero 0.6847, league base rate 0.6824, naive
  trailing-10 0.6930, dev n = 539. Per-season LL@3.5 — SHRINK:
  2022 0.6816, 2023 0.6760, 2024 0.6808, 2025 0.6856; Gate Zero:
  2022 0.6869, 2023 0.6829, 2024 0.6848, 2025 0.6843 (sign check
  3 of 4 for SHRINK). The recomputation must reproduce SHRINK
  beating BOTH baselines within artefact rounding; if it does
  not, the candidate STOPS: no sealed read, verdict written as
  a STOPPED report explaining the discrepancy.
- If SHRINK passes the dev gate, the dev-pass token is recorded
  via gate_lib (`record_dev_pass`, candidate id `L1-K-FO`)
  BEFORE any sealed load. If SHRINK does not pass, the candidate
  dies at dev and the window stays unread.

## Virgin protocol

- Virgin window: season "2026" (n = 135, complete) — the
  original virgin season named in the original prereg and in
  `league/FO-PremierLeague/config.yaml`. Mechanical token for
  gate_lib parsing: virgin_primary: 2026
  Read **ONCE**, only if
  SHRINK passes the dev gate, after the dev-pass token is
  recorded, loaded through the gate_lib sealed loader
  (`load_sealed_rows`). One fresh online pass over 2021–2026;
  predictions for 2026 use only earlier matches; r per the
  discipline above.
- Calibration per arm at 3.5 via gate_lib: predicted − actual
  (mean predicted P(over 3.5) − actual over rate), in percentage
  points, with SE = sd(pred_i − y_i)/√n reported. (The gate uses
  |breach|, so the legs are identical under the gate_lib sign
  convention, predicted - actual.)

## GATE LEGS (verbatim, frozen — identical to PREREG_K_FO)

Dev gate — pooled dev LL@3.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@3.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over 3.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Reading of the legs, fixed here so the verdict is mechanical:

- An arm *passes* iff it survives the dev gate AND passes virgin
  legs (i)–(ii) (a PROVISIONAL PASS counts as a pass, recorded as
  such) AND, for the variant arm SHRINK only, leg (iii): SHRINK's
  dev LL@3.5 ≤ Gate Zero's in at least half the scored dev
  seasons (≥2 of 4). Gate Zero is exempt from (iii) (it is the
  comparator); for Gate Zero, leg (i) reads LL@3.5 ≤ the best
  baseline's.
- An arm that fails the dev gate is dead under the original
  reading: it is not read on the virgin window. Under this Lane 1
  entry the dev gate is judged on the arm of record, SHRINK, and
  Gate Zero is run on the sealed window solely as the leg-(i)
  reference, exactly as stated above.
- If Gate Zero and SHRINK both pass, the lower pooled virgin
  LL@3.5 ships; a tie goes to Gate Zero (simpler arm). If only
  one passes, it ships. If none passes, K-FO verdict is FAIL and
  nothing ships.

Lane 1 reading (adapted only where the arm-of-record designation
requires it): the dev gate is judged on the arm of record,
SHRINK — pooled dev LL@3.5 of SHRINK must beat BOTH baselines,
else SHRINK is dead and there is no sealed read. Leg (iii) =
SHRINK's dev LL@3.5 ≤ Gate Zero's in at least half the scored
dev seasons (≥2 of 4). The both-pass rule is retained verbatim:
Gate Zero's dev failure is a reproduced fact under this
preregistration's own dev evaluation, so the both-pass branch
cannot trigger unless the dev recomputation contradicts the
documented numbers — in which case the candidate STOPS under
the dev protocol above and no sealed read occurs. SHRINK passes
iff it survives the dev gate AND passes virgin legs (i) and
(ii) (PROVISIONAL counts on leg (ii), recorded as such) AND leg
(iii). Verdict labels: all legs clean → CLEAN PASS; leg (ii)
provisional with (i) and (iii) passed → PROVISIONAL PASS;
otherwise FAIL. If SHRINK passes, it ships (subject to the
runner-join preparation on this branch; no merge under this
preregistration).

## Operational check (carried over from the original prereg)

Referee identity coverage is **0/810** matches:
`content.matchFacts.infoBox.Referee.text` is empty in every
payload. No referee arm exists (feature X8 DROPPED at the data
level in `analysis/FEATURES.md`), and none can be added without
a new preregistration and a new data source. There is no referee
operational gate and no referee fallback for this candidate,
because SHRINK uses no referee data at all.

## Reporting requirements

- P6 worst-fold: the verdict reports the worst dev season's legs
  (worst by the reference arm, Gate Zero, at the primary line)
  beside the pooled legs, produced by `league/worst_fold/` —
  information only, no gate change.
- P2 seal: all artefacts produced under this preregistration are
  computed on dev-era seasons only until the single sealed read;
  the verdict states the prereg commit hash and the dev-pass
  token record.
- Verdict: `league/FO-PremierLeague/reports/VERDICT_L1_K_FO.md`,
  with the documented vs recomputed dev numbers and, if read,
  every sealed leg.

## Outputs

- Engine: `league/FO-PremierLeague/engine/cards/` (existing;
  Lane 1 runner `run_l1_k_fo.py` added).
- Dev results: `league/FO-PremierLeague/engine/cards/results_dev_l1.json`.
- Virgin results: `league/FO-PremierLeague/engine/cards/results_virgin_l1.json`
  (or a `{"virgin_read": false, ...}` marker when virgin is not
  read).
- On PASS only: fitted parameters for the virgin fit
  `league/FO-PremierLeague/engine/cards/fitted_params_virgin_l1.json`
  (HL, K_PRIOR, r per method, league means and per-team shrunk
  rates at the 2026 cutoff) and virgin predictions
  `league/FO-PremierLeague/predictions/k_fo_virgin_predictions.csv`
  — the shipped arm's (SHRINK's) predictions, one row per 2026
  match: expected home/away/total yellows, FT ladder P(over
  1.5 / 2.5 / 3.5 / 4.5), and 1H/2H splits via the frozen cards
  constant 0.348 (1H mean = 0.348·FT mean, 2H mean = 0.652·FT
  mean; 1H lines 0.5/1.5/2.5, 2H lines 1.5/2.5/3.5, same NB r).
  Halves are presentation only, never fitted.

## Forbidden

Any gate move after results are seen; any second sealed read;
any arm beyond Gate Zero/SHRINK; any constant search on this
corpus. Production code and data are untouched. No push. No merge.
