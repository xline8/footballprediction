# Verdict — K-SCO (Scotland Premiership cards) — **FAIL** (dev gate; virgin NOT read)

Prereg: `prereg/PREREG_K_SCO.md`. Primary line 3.5. Gate Zero only
(X8 referee arm dropped in FEATURES: split-half r = 0.158).

## Dev (pooled LL@3.5, n=684)
| | LL@3.5 |
|---|---|
| Gate Zero model | 0.6906 |
| League base rate | **0.6904** |
| Naive trailing-10 | 0.6916 |

The model beats the naive baseline but **loses to the plain league
base rate by 0.0002 LL** — the dev gate requires beating BOTH
baselines, so Gate Zero is dead at dev. Per the frozen rule the
virgin window (2025/2026) was **deliberately NOT read** and stays
unburned. Nothing ships; no predictions CSV.

A FAIL by two ten-thousandths is still a FAIL: the gate is the
gate. (For the record: SCO yellows run 3.59–3.99/match with the
weakest target-trait reliability in this league, r = 0.639, and no
referee signal to add — the base rate is simply hard to beat here.)
