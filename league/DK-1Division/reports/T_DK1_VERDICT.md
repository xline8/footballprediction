# T-DK1 verdict — PROVISIONAL PASS (X5 ships)

Primary line 26.5. Dev (seed/tuning 2022/2023, scored 2023/2024–
2024/2025, n=384): Gate Zero LL 0.6572, X5 0.6534, X7 0.6572 (the
fitted X7 box-touch beta was 0.0 on the tuning window, so X7 was
numerically identical to Gate Zero); base-rate 0.6951, naive
trailing-10 0.6616. Gate Zero beats both ⇒ dev gate PASS; virgin
read once. Virgin-fit parameters (causal, pre-virgin data only):
lambda and r re-tuned on 2022/2023–2024/2025 (see results_virgin.json).

Virgin 2025/2026 (n=192), read once:

| Arm | LL | Calibration (pp) | SE (pp) |
|---|---:|---:|---:|
| Gate Zero | 0.6786 | −0.77 | 3.56 |
| X5 | 0.6764 | −1.70 | 3.55 |
| X7 | 0.6786 | −0.77 | 3.56 |
| Base rate | 0.6866 | — | — |

Gate arithmetic: Gate Zero passes all legs with clean calibration
(−0.77pp). X5 also passes all legs (LL 0.6764 ≤ Gate Zero and ≤ base;
sign leg ✓; calibration |−1.70|pp within 1 SE of the boundary ⇒
provisional-grade). Both-pass rule: the lower pooled virgin LL ships
⇒ X5 ships, and the candidate's recorded verdict is PROVISIONAL
(the shipped arm's calibration grade). Predictions in
predictions/t_dk1_virgin_predictions.csv (1H/2H via frozen share
0.461). Numbers independently recomputed by the coordinator — exact
match.
