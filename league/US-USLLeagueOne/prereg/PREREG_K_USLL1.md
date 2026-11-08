# Pre-registration — K-USLL1 (USL League One cards model, unified yellows)

Frozen: 2026-11-10, before any fitting. Branch `build/us-usll1`.
Design authority: `league/US-USLLeagueOne/analysis/MODEL_DESIGN.md` §4;
features per `league/US-USLLeagueOne/analysis/FEATURES.md` (X5 base;
X8 arm); evidence per `league/US-USLLeagueOne/analysis/EDA.md`
(F2/F5/F7). Reference: production `model_cards.py` via the J1 engine
`league/J1/engine/cards/` (as ported in `league/US-MLS/engine/cards/`).
**Calibration = actual − predicted** throughout.

## Target and lines

- Target: total unified yellows = `yellow_home + yellow_away` (**stats
  feed**, `cards_source="stats"` for every row), scored ONLY on rows with
  `cards_target_valid` (F5 artefact freeze: stats-feed yellows are broken
  in 2021–22 — means 0.88/1.49 with 79.8%/71.8% zero-card matches — AND
  the event feed carries no card events at all in 2021–2025, so no valid
  card target exists before 2023 in either feed; this is the reverse of
  the USL Championship pattern, where the stats feed was correct. From
  2023 the stats feed is plausible: means 4.78/5.34/5.03). **Primary
  line 5.5** (dev 2023–2024 over-rate 0.406; the 4.5 line sits at 0.607 —
  5.5 is closest to 0.5, |0.406−0.5|=0.094 < |0.607−0.5|=0.107). Ladder
  4.5 / 5.5 / 6.5. All gate legs use binary LL at 5.5.

## Reference architecture (all arms share)

Exactly as PREREG_K_J1's harness: per-match online walk-forward
(predict-then-update), team card ratings with the production
decay/shrinkage pattern, NB count distribution with the engine's fitted
r, and ensemble with the naive trailing-10 as in the J1 cards engine.

## Arms

1. **Gate Zero (GZ)** — reference pattern, no referee.
2. **Arm X8 (referee covariate)** — GZ plus the referee strictness
   covariate (X8, F7 r = .379 at the ≥10-match threshold — 13 referees,
   496 valid regular matches; only 1 referee reaches ≥20 matches, so the
   sibling's ≥20 screen is not estimable here), constructed exactly as K-J1's X8 arm:
   trailing referee mean of unified yellows within this league, shrunk
   toward the league mean with the engine's frozen shrinkage; referees
   with <8 prior in-league matches take the shrunk league mean. A
   fixture whose referee is missing falls back to Gate Zero, with no
   imputation. Referee coverage is 95.4% / 92.1% in dev 2023–2024 and 95.9% in virgin
   2025 (0% in 2021, which is outside this candidate's windows entirely).

## Baselines

League base rate (prior-seasons over-5.5 rate, from valid rows only) and
naive trailing-10 through the same NB, at the 5.5 line.

## Dev protocol

COLD START at the 2023 opener: no valid card target exists before 2023,
so there is no warm-up — team/referee state builds walk-forward from the
first valid match. Scored dev seasons 2023, 2024 (n=313 valid regular
rows: 191 + 122; ten 2024 regular matches are excluded — 8 with stats but
no yellow_cards key, 2 without stats). The dev harness must not read
2025 rows at all or any 2026 rows, and must not read cards-invalid rows
as target or state updates.

## Virgin protocol

Season 2025 (n=210 valid regular rows), read ONCE, only for dev-passing
arms, online walk-forward continuing from the dev end state. Calibration
= actual over-rate − mean P(over 5.5), SE reported.

## GATE LEGS (verbatim, frozen — identical across the program)

Dev gate — pooled dev LL at the primary line beats BOTH baselines (league base rate; naive trailing-10 / climatology), else arm dead, no virgin read. Virgin legs — (i) LL ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |actual − predicted| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass (variant dev LL ≤ Gate Zero's in at least half the dev seasons; Gate Zero exempt). Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL. Ties → simpler arm (Gate Zero first). If Gate Zero fails its own dev gate, the variants are moot — verdict FAIL regardless of variant dev numbers, and the virgin window is not read.

For this candidate the "primary line" in the gate text is 5.5 and LL
means binary log-loss at 5.5. The dev per-season sign check in leg (iii)
is read over the two scored dev seasons (2023, 2024): at least 1 of 2.

## Operational condition

Referee assignment must be known at prediction time in the live pipeline;
warehouse records are post-match snapshots and cannot prove pre-match
publication. The no-imputation fallback above is the operating rule
regardless of the verdict.

## Forbidden

Red-card target modelling (R12); halves modelling (presentation via
frozen constant 0.373 only); absence features; snapshot features; any use
of the event-feed card counts as the target (F5).

## Outputs

- Engine: `league/US-USLLeagueOne/engine/cards/`; `results_dev.json`
  (+ CSV), `results_virgin.json`, `fitted_params_virgin.json`.
- Virgin predictions: `league/US-USLLeagueOne/predictions/k_usll1_virgin_predictions.csv`
  (shipped arm; GZ labelled if nothing ships): match_id, date, teams,
  actual total unified yellows, exp_yellows_total, referee, FT ladder
  P(over 4.5/5.5/6.5), 1H/2H ladders presentation-only via frozen constant
  0.373 with the arm's NB r (1H lines 0.5/1.5/2.5; 2H lines 1.5/2.5/3.5).
- Verdict: `league/US-USLLeagueOne/reports/K_USLL1_VERDICT.md`.
