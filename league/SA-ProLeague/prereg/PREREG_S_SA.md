# Pre-registration — S-SA (SA-ProLeague shots-on-target model)

Frozen: 2026-11-09, before any fitting. Branch `build/sa-proleague`.
Design authority: `analysis/MODEL_DESIGN.md` (S-SA); features X5
base, X4 quality input (FEATURES.md); evidence F1b/F2/F6. Reference:
production `model_sot.py` v5; J1 analogue `PREREG_S_J1.md` — the v5
architecture constants there are carried over verbatim (ridge
lambda = 100, HL = 365, lazy refit 7 days, total-shots ratings
prior K = 8, Beta-Binomial prior P = 200, ensemble 50/50 with naive
trailing-10, NB size r = 79.94 frozen). Engine port:
`league/SCO-Premiership/engine/sot/`. X6 (xGOT) is NOT an arm: its
population era starts 2024/2025, inside the last dev season, so it
cannot be honestly dev-tested across the dev window (FEATURES).

- Target: total SOT = `ShotsOnTarget_home + ShotsOnTarget_away`
  (stats feed, 100% in every season). Primary line **8.5** (dev
  over-rate 0.546, closest to 0.5). Ladder 7.5 / 8.5 / 9.5
  reported, gate at 8.5.
- Arms: **Gate Zero** (v5 unmodified); **RS** (Gate Zero with the
  BB prior raised P = 200 → 20,000); **X4** (Gate Zero with the BB
  ratio replaced by `rho_venue · (q_team/q_league)` clamped
  [0.15, 0.50], q = Σ sm_xg / Σ sm_shots over trailing 25 shotmap
  matches, min 8 else Gate Zero fallback; exactly as PREREG_S_J1
  arm X4). SA shotmap exists only from 2023/2024, so X4 is inactive
  before the era by its own min-8 rule.
- Walk-forward: per-match, chronological (date, match_id),
  predict-then-update, date-grouped (same-date matches never see
  each other). Warm-up: 2021/2022 + 2022/2023 update state, never
  scored (pre-break seasons are warm-up only, per MODEL_DESIGN).
- Dev: scored seasons **2023/2024–2024/2025 (n = 612)**. The dev
  harness must not read 2025/2026 or 2026/2027 rows at all.
- Baselines: league base rate (prior-seasons over-8.5 rate,
  constant within target season); naive trailing-10 through the
  same NB.
- Virgin: 2025/2026 (n = 306), read ONCE, only for dev-passing
  arms, continuing from the dev end state. Calibration = mean
  P(over 8.5) − actual rate, SE = sd(p_i − y_i)/√n. 2026/2027 NOT
  read (reserved confirmatory).

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev LL@8.5 beats BOTH baselines (league base rate; naive trailing-10), else arm dead, no virgin read. Virgin legs — (i) LL@8.5 ≤ Gate Zero's and ≤ best baseline's; (ii) calibration |mean P(over 8.5) − actual| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass. Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading: an arm passes iff it survives the dev gate AND
passes virgin legs (i)–(ii) (PROVISIONAL counts) AND, for variants,
leg (iii) — variant dev LL@8.5 ≤ Gate Zero's in at least half of
the dev seasons (≥1 of 2). Ties → simpler arm (Gate Zero, RS, X4).
If Gate Zero fails its dev gate, variants are moot, verdict FAIL,
virgin NOT read.

## Outputs

Engine `engine/sot/`; `results_dev.json` (+ CSV);
`results_virgin.json`; `fitted_params_virgin.json`; on PASS,
`predictions/s_sa_virgin_predictions.csv` (shipped arm; FT ladder
7.5/8.5/9.5 ensemble probabilities; 1H/2H ladders presentation-only
via frozen SOT constant 0.4469, NB r = 79.94, lines 1H 3.5/4.5/5.5,
2H 4.5/5.5/6.5). Verdict `reports/S_SA_VERDICT.md`.
