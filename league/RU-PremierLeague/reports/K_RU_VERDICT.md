# Verdict — K-RU (RU-Premier League cards)

**FAIL. Nothing ships.**

Prereg: `prereg/PREREG_K_RU.md`. Target: EVENT-UNIFIED yellows
(the stats-vs-events artefact is present in this league: exact
agreement 76.5%, mean stats − events = −0.550). Primary line 4.5.
Gate Zero only (X8 dropped at design: referee reliability
r = 0.178 pooled, season-unstable). All numbers recomputed by the
coordinator from the per-match CSVs and match the engine JSONs.
The cards NB size r is estimated from the 2021/2022 warm-up
predictions only (dev r: model 32.23 / base 37.98 / naive 33.38);
the dev harness loads no virgin rows.

## Dev (n = 720, LL @ 4.5)

| method | pooled | 2022/2023 | 2023/2024 | 2024/2025 |
|---|---|---|---|---|
| Gate Zero | 0.6812 | 0.6759 | 0.6742 | 0.6934 |
| league base rate | 0.6860 | | | |
| naive trailing-10 | 0.6976 | | | |

Dev gate: 0.6812 beats both baselines — PASS (narrowly vs base).

## Virgin (2025/2026, n = 240, read once)

| method | LL @ 4.5 |
|---|---|
| Gate Zero | 0.6869 |
| league base rate | 0.6814 |
| naive trailing-10 | 0.6939 |

Leg (i): 0.6869 ≤ best baseline 0.6814? **No — FAIL.** Leg (ii):
actual over-4.5 rate 0.4167, mean predicted 0.4427, calibration
−2.60 pp, SE 3.21 pp — the excess (1.60 pp) is within 1 SE, so
leg (ii) alone would be a provisional pass, but leg (i) is
decisive. Verdict FAIL, nothing ships. The dev edge over the base
rate (+0.0048) did not survive the virgin season.
