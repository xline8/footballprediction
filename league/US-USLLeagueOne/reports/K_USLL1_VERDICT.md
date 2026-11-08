# K-USLL1 Verdict — USL League One cards model

Date: 2026-11-10. Prereg: `prereg/PREREG_K_USLL1.md`. Engine: `engine/cards/`.

## Verdict: FAIL — dev gate; virgin not read

At the frozen primary line 5.5, Gate Zero loses to BOTH baselines
pooled (0.684710 vs base 0.681311 and naive 0.680838). X8 is moot under
the frozen gate order and also loses to both baselines. No virgin
command was run and nothing ships.

## Dev results (2023–2024 cards-valid regular, n=313; LL@5.5)

Cold start at the 2023 opener (no valid card target exists before
2023: the stats feed is broken in 2021–22 and the event feed carries
no card events in 2021–2025 — see prereg). NB r per method estimated on
the 2023 scored records (model 30.42, base 28.86, naive 29.47).

| Season | n | GZ | X8 | Base rate | Naive t-10 |
|---|---:|---:|---:|---:|---:|
| 2023 | 191 | 0.680721 | 0.680196 | 0.678086 | 0.691236 |
| 2024 | 122 | 0.690955 | 0.689911 | 0.686361 | 0.664559 |
| **Pooled** | **313** | **0.684710** | **0.683983** | **0.681311** | **0.680838** |

Referee coverage in the scored frame: 95.8% (2023), 91.8% (2024). X8
improves on GZ in both seasons but not enough to reach either
baseline; the league base rate is the strongest predictor in this
frame — team/referee card structure at the 5.5 line is weaker than
the pooled rate in a league whose valid history is two seasons.

## Per-leg verdicts

| Leg | GZ | X8 |
|---|---|---|
| Dev gate versus both baselines | FAIL (0.684710 > 0.680838) | FAIL (0.683983 > 0.680838; moot) |
| Virgin | not read | not read |
| **Overall** | **FAIL** | **FAIL (moot)** |

## What ships

Nothing. No virgin predictions file exists. Verification: no cards
virgin command was run.
