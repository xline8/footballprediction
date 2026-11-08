# Verdict — S-HR (HR-HNL shots on target): **FAIL (virgin legs i and ii)**

Frozen gates: PREREG_S_HR.md (e9872c4, before any fitting). Primary line 7.5,
ladder 6.5 / 7.5 / 8.5.

## Dev (warm-up 2021/2022; scored 2022/2023–2024/2025, n = 540 stats rows)
Pooled LL@7.5: Gate Zero **0.670835**, RS **0.669972** vs league base rate
0.701515, naive trailing-10 0.675865 → **both arms pass the dev gate**.
RS's dev sign check passes (≤ GZ in 2022/2023 and 2023/2024, worse in
2024/2025 — 2 of 3).

## Virgin 2025/2026 (n = 180) — read ONCE, for both dev-passing arms
| | LL@7.5 | calibration diff | SE |
|---|---|---|---|
| Gate Zero | 0.685361 | −5.14pp | 3.69pp |
| RS | 0.686073 | −5.16pp | 3.69pp |
| League base rate | **0.675772** | −1.67pp | |
| Naive trailing-10 | 0.684528 | −4.63pp | |

Leg (i): an arm's LL must be ≤ Gate Zero's AND ≤ the best baseline's.
**Both arms lose to the league base-rate baseline (0.675772)** → leg (i)
FAILS for both arms. Leg (ii) also fails outright: |−5.14pp| exceeds
the 1.0pp boundary by more than 1 SE (5.14 > 1.0 + 3.69 = 4.69) for
Gate Zero, and likewise for RS (5.16 > 4.69). → **FAIL. Nothing ships.**

Independent verification: the league base-rate baseline was recomputed
from the league CSV — pre-virgin over-7.5 rate 0.577778 over 720
matches, virgin actual over-rate 0.594444, baseline LL 0.675772 and
calibration −1.67pp, all exact. (The HR harness's virgin baselines are
scored on the virgin window itself; see the engine commit note on the
inherited FI defect that was corrected here before any fitting.)

Diagnosis (recorded, not acted on): the virgin was a high-SOT season
relative to the model's state (actual over-7.5 rate 0.594 vs the dev
era's 0.552) and both arms under-predicted by ≈5pp — the v5 pattern's
ratings, anchored on the low 2024/2025 dev season (7.478 SOT/match),
lagged the rebound to 8.156. A constant pre-virgin rate was closer.
