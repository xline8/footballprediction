# Pre-registration — Lane 1 — K-NO-OBOS (NO-OBOSLigaen cards model, yellows)

Frozen: 2026-11-11, before any sealed (2026) access in this
worktree. Branch `build/lane1-knoobos`. This is a NEW candidate
under the Improvement Program's Lane 1 (unread sealed windows),
`league/IMPROVEMENT_PROGRAM.md`: the original candidate
(`prereg/PREREG_K_NO_OBOS.md`, verdict
`reports/K_NO_OBOS_VERDICT.md`) failed at the DEV gate and its
sealed window was deliberately NOT read, so season 2026 remains
genuinely sealed for this candidate. One read, verdict final,
no iteration against the window after the read.

Design authority: the original prereg (frozen 2026-11-10),
`MODEL_DESIGN.md` §4, `FEATURES.md` (X5 base; X8 arm), `EDA.md`
(F2/F8), and the Lane 1 wave-1 cohort design
(`league/improvement_scratch/LANE1_WAVE1/cohort_report.md` §1.5).
Reference: production `model_cards.py` via the NO-Eliteserien
engine `league/NO-Eliteserien/engine/cards/` (model.py copied;
pattern unchanged), as in the original. The OBOS CSV carries
the referee name directly (`referee` column), as in
NO-Eliteserien.

## The method difference (stated in advance, the only one)

- **Arm of record = X8 (referee covariate).** X8 becomes the
  reference architecture for this entry, exactly as constructed
  in the original prereg and the frozen engine (see Arms).
- **Gate Zero is retained as a baseline only.** Its dev numbers
  are recomputed and reported, and its sealed numbers are
  computed as the comparator for virgin leg (i) and the sign
  check, but its dev pass is NO LONGER a precondition for the
  arm of record's sealed read. That precondition is the
  gate-architecture defect this Lane 1 entry corrects: in the
  original run Gate Zero scored dev LL@3.5 0.6693, beating the
  naive trailing-10 (0.6729) but losing to the league base rate
  (0.6683) by 0.0010, which made X8 moot by rule even though
  X8 scored dev LL@3.5 0.6553, beating both baselines. The
  original verdict itself named this remedy ("a future prereg
  that promotes the referee arm to the reference position").
- No other method difference. Target, lines, tolerances,
  baselines, arms' construction, and gate-leg semantics are
  identical to the original prereg (below).

## Target — frozen with its reason (unchanged from the original)

- Target: total yellows = `yellow_home + yellow_away`,
  **event-feed unified** (Yellow + YellowRed events per side;
  PREPROCESSING rule 7; events present for 100% of matches).
  The stats feed carries no yellow_cards key at all in any
  season of this league, so no stats target exists; the event
  feed is the single source, frozen as such.
- **Primary line: 3.5** (dev over-rate 38.65%; dev mean 3.19).
  Ladder 2.5 / 3.5 / 4.5. All gate legs use binary LL at 3.5.

## Arms

1. **Gate Zero (GZ)** — reference pattern, no referee.
   Baseline / comparator only under this entry (see above);
   it cannot ship under this preregistration.
2. **Arm of record — X8 (referee covariate)** — Gate Zero plus
   the referee strictness covariate (X8, F8 r=0.715),
   constructed exactly as the frozen engine implements it:
   trailing referee mean of unified yellows within this
   league, shrunk toward the league mean with K_REF = 8
   (`rate = (sum of prior yellows + K_REF * league_mean) /
   (n_prior + K_REF)`), multiplier `rate / league_mean`
   clamped to [0.67, 1.50]. A fixture whose CSV referee is
   missing (unknown identity) or whose referee has <8 prior
   in-league matches falls back to the Gate Zero prediction
   for that match (no imputation). Coverage is reported per
   season (original prereg: virgin 229/240 = 95.4%; 2021 has
   no named referees at all and is warm-up only).

## Baselines

League base rate (prior-seasons over-3.5 rate) and naive
trailing-10 through the same NB — as the original harness
computes them, at the 3.5 line.

## Dev protocol

Warm-up 2021 (updates state, never scored); scored dev
2022–2025 (n=960). The dev harness must not read 2026 rows
(`league/gate_lib/` `assert_no_sealed_rows` on the dev load).
Dev evaluation runs through `league/gate_lib/`; the arm of
record's dev pass is recorded as a dev-pass token in the
gate_lib registry before any sealed load, and the sealed
rows are loaded only through the fail-closed sealed loader
(`load_sealed_rows`).

## Sealed (virgin) protocol

virgin_primary: 2026
Season 2026 (complete regular season, n=240), read ONCE,
only if the arm of record passes the dev gate below, online
walk-forward continuing from the dev end state. Both arms
(X8 and Gate Zero) and both baselines are computed on the
window, Gate Zero as comparator only.
Calibration = mean P(over 3.5) − actual over-rate, in the
gate_lib sign convention: predicted - actual
(predicted − actual), SE reported.

## GATE LEGS (identical to the original prereg, applied as pinned in §1.5 of the cohort report)

Dev gate — the arm of record's pooled dev LL at the primary line beats BOTH baselines (league base rate; naive trailing-10 / climatology), else the arm is dead, no sealed read. (Gate Zero's own dev result no longer gates anything; it is recomputed and reported.)
Virgin legs — (i) LL ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check (arm-of-record dev LL ≤ Gate Zero's in at least half the dev seasons; Gate Zero exempt).
Both-pass semantics, where applicable: the original both-pass
comparison is retained as virgin leg (i) — the arm of record
must be at or below Gate Zero's sealed LL to ship, so a
shipping X8 is by construction the lower-LL arm; Gate Zero
itself is a baseline under this entry and does not ship.
Verdict classes: all legs pass with calibration inside the
1.0pp tolerance = CLEAN PASS; all legs pass except
calibration, whose breach is within 1 SE of the boundary =
PROVISIONAL PASS; otherwise FAIL. One read, verdict final.

## Design seal (P2) and worst-fold (P6)

- EDA/design artefacts for this entry are under the P2 design
  seal: no new EDA or reliability artefact is computed for
  this entry from sealed-season data, and no design decision
  in this preregistration is drawn from the sealed season's
  contents. The design is the original frozen design; method
  knowledge drawn from other leagues' failures and from this
  candidate's own DEV record is permitted Lane 1 learning.
- The verdict includes the P6 worst-fold block: the worst
  dev season's legs (fold defined by the reference arm, per
  `league/worst_fold/`) reported beside the pooled legs,
  information only, no gate change.

## Operational condition (as K-J1, carried over verbatim in substance)

Referee assignment must be known at prediction time in the
live pipeline; warehouse records are post-match snapshots
and cannot prove pre-match publication. The no-imputation
fallback above is the operating rule regardless of the
verdict. A PASS ships with this condition attached, and
runner-join preparation must separately count upcoming
fixtures carrying referee names and report that count
plainly.

## Forbidden (unchanged)

Red-card target modelling (R12); halves modelling
(presentation via frozen constant 0.306 only); absence
features; snapshot features; any target other than the
event-unified yellows above.

## Outputs

- Lane 1 dev artefact: `league/NO-OBOSLigaen/engine/cards/results_dev_l1.json`
  (the frozen `results_dev.json` is not overwritten).
- Lane 1 sealed artefact: `league/NO-OBOSLigaen/engine/cards/results_virgin_l1.json`,
  plus `fitted_params_virgin_l1.json` if an arm ships.
- Virgin predictions (shipped arm only, if PASS):
  `league/NO-OBOSLigaen/predictions/k_no_obos_l1_virgin_predictions.csv`
  in the original prereg's column pattern (match_id, date,
  teams, actual total yellows where the harness pattern
  carries it, exp_yellows_total, referee, FT ladder
  P(over 2.5/3.5/4.5), 1H/2H ladders presentation-only via
  frozen constant 0.306 with the arm's NB r).
- Dev-pass registry: `league/NO-OBOSLigaen/engine/cards/dev_pass_registry_l1.json`.
- Verdict: `league/NO-OBOSLigaen/reports/K_NO_OBOS_L1_VERDICT.md`,
  recording all leg numbers (dev + sealed), the P6
  worst-fold block, and this preregistration's commit hash.
