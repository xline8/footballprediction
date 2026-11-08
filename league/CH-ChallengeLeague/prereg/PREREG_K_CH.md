# Pre-registration — K-CH (CH-ChallengeLeague cards model)

Frozen: 2026-11-10, before any fitting. Design authority:
`analysis/MODEL_DESIGN.md` (K-CH); feature X5; evidence F1/F2/F5.
TARGET FREEZE (reason written, before fitting): the CH stats feed
publishes card keys from 2023/2024 onward, while the event feed
carries almost no card events in 2021/2022–2025/2026 (85 event
yellows in the entire dev era; exact stats-vs-events agreement
10.6%, mean difference +4.12/match — the event feed is absent, not
disagreeing). The target is therefore **stats-feed total yellows**
(`yellow_cards_home + yellow_cards_away`) for dev AND virgin — the
mirror image of FI's coverage-forced choice. NO X8 arm: no referee
field exists in the parsed payload structure. Single-arm candidate.

- Target: total stats yellows. Primary line **4.5** (dev over-rate
  0.606; 5.5 gives 0.383, so 4.5 is closest to 0.5). Ladder 3.5 / 4.5 /
  5.5 reported, gate at 4.5.
- Arm: **Gate Zero** only.
- Pattern: trait-rate Negative Binomial (documented minimal port of the programme's count pattern; production engine code is not runnable from this bundle — divergence recorded in MODEL_DESIGN.md). Per-match chronological walk-forward (date, match_id), date-grouped predict-then-update.
- Traits: for each team, decay-weighted (HL = 365 days) sums of target for/against over prior target-present matches; rate = (Σ w·x + K·μ_side) / (Σ w + K), K = 8, μ_side = decay-weighted league per-team mean over prior target-present matches. λ_team = for_rate(team) × against_rate(opp) / μ_side; μ_match = λ_home + λ_away.
- Distribution: Negative Binomial with size r fitted on the DEV scored walk-forward rows only (grid r ∈ {2..60, 80, 100}, max NB log-likelihood at the Gate Zero μ's), frozen before the virgin run.
- Baselines: league base rate = over-rate over all target-present matches strictly before the scored window (dev: warm-up era; virgin: warm-up + dev), as a constant Bernoulli p; naive trailing-10 = mean total of the last 10 target-present league matches before the match, through the same NB size r.
- Warm-up: 2023/2024 (180 stats rows, state only, never scored). Dev scored: 2024/2025 (n = 180). Dev harness must not read 2025/2026 rows.
- Virgin: 2025/2026 (n = 181), read ONCE, only if Gate Zero passes dev. Calibration = mean P(over primary) − actual rate, SE = sd(p_i − y_i)/√n.

## GATE LEGS (verbatim, frozen)
Dev gate — pooled dev LL at the primary line beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over) − actual| ≤ 1.0pp clean PASS, breach within 1 SE = PROVISIONAL PASS, else FAIL; (iii) dev per-season sign check for both-pass (vacuous: single-arm candidate). Both-pass: lower pooled virgin LL ships; one → ships; none → FAIL. Ties → simpler arm. If Gate Zero fails its dev gate, verdict is FAIL and the virgin is NOT read.
(Single arm: Gate Zero passes iff it survives the dev gate AND virgin legs (i)–(ii).)

## Outputs
Engine `engine/cards/`; `results_dev.json` (+ CSV); `results_virgin.json`;
on PASS, `predictions/k_ch_virgin_predictions.csv` (FT ladder; 1H/2H
presentation via frozen yellows constant 0.3399). Verdict `reports/K_CH_VERDICT.md`.
