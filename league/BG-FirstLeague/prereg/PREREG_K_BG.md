# Pre-registration — K-BG (Bulgaria First Professional League cards model)

Frozen: 2026-11-10, before any fitting. Branch `build/bg-first`.
Design authority: `analysis/MODEL_DESIGN.md` (K-BG); features X5, X8
(FEATURES.md); evidence EDA (event yellows for 0.229 / against
0.334 — weak, recorded; referee strictness split-half r = 0.379,
20 referees ≥20 matches, coverage ~100%). Reference: production
`model_cards.py`; sibling analogue `league/RU-1Division/prereg/
PREREG_K_RU1.md` — the architecture (decayed team yellow ratings +
count distribution + naive ensemble, shared cards model with its
built-in referee-multiplier path) is carried over in form, changing
only league, seasons, line and the arm set below.
Phase rule (frozen): all phases in every window, flagged; no phase
feature. Team identity is the FotMob team id.
Calibration = **actual − predicted** everywhere in this build.

- Target: total **event-unified yellows** = `yellow_home +
  yellow_away` (direct Yellow + YellowRed events per side).
  Target-source decision (frozen here, before fitting, evidence in
  DATA_UNDERSTANDING Step 1): the stats feed publishes **no
  yellow_cards key at all** in any season, so no stats target and
  no stats-vs-events artefact exist in this league; the event feed
  is complete (events in 1,471/1,471 matches, plain Yellow events
  abundant in every season, dev and virgin alike). The event-unified
  target is therefore used in dev AND virgin for gate
  comparability. Primary line **4.5** (scored-dev over-rate 0.561,
  closest to 0.5; 5.5 → 0.421). Ladder 3.5/4.5/5.5 reported.
- Arms: **Gate Zero** (reference unmodified; referee not used);
  **X8** — Gate Zero plus the shared model's referee multiplier:
  the appointed referee's trailing in-league mean unified yellows,
  shrunk toward the league mean with K_REF = 8, multiplier clamped
  [0.67, 1.50], applied only when the referee has ≥8 prior
  in-league matches (else that match falls back to Gate Zero
  exactly). Referee identity = `content.matchFacts.infoBox.
  Referee.text` as stored in the CSV `referee` column; only matches
  strictly before kickoff count.
- Training warm-up 2021/2022; dev scored 2022/2023–2024/2025
  (rows with the target n = 859); dev harness must not read
  2025/2026 / 2026/2027 rows.
- Baselines: league base rate; naive trailing-10 through the same
  count distribution as the reference harness.
- Virgin: 2025/2026 (n = 293), read ONCE, only for arms passing
  the dev gate. Calibration at 4.5 = actual − mean predicted,
  SE = sd(y_i − p_i)/√n.
- Halves: 1H/2H presentation via the frozen yellow-cards constant
  0.3183 (event times — the legitimate halves source here).

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@4.5 beats BOTH baselines (league base rate; naive trailing-10), else the arm is dead, no virgin read. Virgin legs — (i) LL@4.5 ≤ Gate Zero's AND ≤ best baseline's (Gate Zero: ≤ best baseline's); (ii) calibration |actual − mean P(over 4.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass (variant dev LL@4.5 ≤ Gate Zero's in ≥2 of 3 dev seasons). Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such)
AND, for the variant, leg (iii). Ties → simpler arm (Gate Zero
before X8). Gate Zero dev failure ⇒ variants moot, FAIL, virgin
NOT read.

## Outputs

Engine `engine/cards/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/k_bg_virgin_predictions.csv` (FT ladder 3.5/4.5/5.5
+ 1H/2H presentation via frozen constant 0.3183). Verdict
`reports/K_BG_VERDICT.md`.
