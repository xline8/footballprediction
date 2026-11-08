# Verdict — C-SAFD corners — FAIL (virgin gate)

Dev used 90 warm-up and 214 scored 2025/2026 matches. Both arms
passed the dev gate; the 2026/2027 partial window was read once and is
TRANSITIONAL (n=94).

| Arm | Dev LL@9.5 | Virgin LL@9.5 | Calibration (SE) |
|---|---:|---:|---:|
| Gate Zero | 0.690279 | 0.672879 | +8.859pp (4.993pp) |
| X7 | 0.694435 | 0.662724 | +8.922pp (4.939pp) |
| League base | 0.711019 | 0.635032 | — |
| Naive trailing-10 | 0.710794 | 0.631062 | — |

Leg (i) fails for both: each is above the best baseline (naive
0.631062), so neither arm is eligible even though X7's virgin LL
(0.662724) is below Gate Zero's (0.672879). Leg (ii) fails: the
breach-plus-SE limits are 5.993pp and 5.939pp, below the observed
breaches. Nothing
ships; no prediction CSV was written. Fitted params are retained as
Gate Zero `reference_label_only`. Both arms are neither clean nor
provisional: both are FAIL. The both-pass/tie rule is therefore not
invoked and the shipped arm is none. Verification: dev n=214, virgin
n=94, phase regular and awarded=0 only, date-grouped state updates, and
no 2024/2025 or virgin rows entered dev fitting. (Independent replay from the engine code reproduces every dev and virgin LL and both calibration figures exactly.)

Verifier's note (coordinator, 2026-11-10): the retained fitted params are the walk-forward fit before the last virgin date (fit_n 382 = 304 dev rows + 78 earlier virgin matches, a legitimate per-date continuation); the file's "training_rows": 304 labels the dev rows only. The virgin window itself is a low-corners regime (actual over-9.5 32.98% vs 44.86% in dev), which is why both arms over-predict by ~8.9pp; the confirmatory read at season end stands.
