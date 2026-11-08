# Step 5 — Features: FI-Ykkosliiga (J1 X1–X9 template)

The J1 causality contract applies: features use only matches strictly before the
target, ratios are ratios of sums, and unavailable values leave the arm inactive.

| Feature | Verdict | FI-Ykkosliiga result |
|---|---|---|
| X1 blend pair (goals+xG) | **ADOPTED — goals-only fallback** | Goals exist in 895/895 payloads; xG is absent in 895/895 and shotmap is empty 895/895. |
| X2 mover tier offset | **ADOPTED** | 18 in-corpus entrants across both directions/origins, 7 from Veikkausliiga and 11 mixed tier-3/unknown; pooled single offset, minimum 3 completed transitions, clamp [0.8, 1.25], first season only. |
| X3 set-play xG share | **DROPPED** | No xG in 895/895 payloads. |
| X4 xG per shot | **DROPPED** | Shotmap empty 895/895. |
| X5 trailing target-rate means | **DROPPED for non-goals** | Stats targets are absent 895/895; event cards have only 11.6%–19.3% coverage in dev seasons. |
| X6 xGOT per shot | **DROPPED** | No shotmap/xGOT in 895/895. |
| X7 opponent-box touches | **DROPPED** | Stats feed empty 895/895. |
| X8 referee yellow rate | **DROPPED** | Referee named 0/162, 0/164, 0/164, 0/135, 0/135 in dev seasons; only 32/135 in virgin 2026. |
| X9 territorial covariates | **DROPPED** | Stats feed empty 895/895. |

Goals 1H presentation uses the frozen pooled dev share **0.4462 (n=718
matches with goals)**. SOT, corners, cards, and total-shots constants are null.
No halves quantity is a feature.
