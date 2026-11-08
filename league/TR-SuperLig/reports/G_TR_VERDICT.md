# G-TR verdict

Source JSONs: `engine/goals/results_dev.json` and `engine/goals/results_virgin.json`. Dev scored 1,033 rows from 2022/2023–2024/2025; virgin scored 306 rows from 2025/2026. No 2026/2027 rows were read.

| arm | dev pooled 1X2 LL | dev RPS | dev OU2.5 LL | dev gate | virgin 1X2 LL | virgin result |
|---|---:|---:|---:|---|---:|---|
| Gate Zero | 1.012636 | 0.210034 | 0.682216 | PASS | 0.996346 | provisional |
| SHRINK | 1.012636 | 0.210034 | 0.682216 | PASS | 0.996346 | provisional |
| X3 | 1.011151 | 0.209624 | 0.681179 | PASS | 0.989127 | provisional |
| climatology | 1.060905 | 0.227729 | 0.689943 | baseline | 1.088239 | baseline |

Dev gate arithmetic: every arm beats climatology on 1X2 LL and RPS and beats the OU baseline (0.689943), so all three pass. X3 beats Gate Zero in 2/3 dev seasons. SHRINK is numerically identical to Gate Zero by construction in this season-blocked harness: unseen (promoted) teams already carry a = d = 0 in log space, and every returning team has ≥6 prior matches, so the prereg's 1–5-prior-match bite never occurs; the arm was evaluated as registered and ties. Virgin LL: X3 ≤ Gate Zero (0.989127 ≤ 0.996346) and ≤ climatology. Calibration: X3 home-win breach +2.534pp, SE 2.670pp → PROVISIONAL PASS; OU2.5 breach −0.860pp, SE 2.866pp → clean PASS. The Gate Zero/SHRINK home-win breaches are +2.364pp (SE 2.673pp), and OU breaches −1.666pp (SE 2.850pp), both provisional. X3 has the lowest passing virgin LL and ships.

Shipped fitted params: `engine/goals/fitted_params_virgin.json` (X3; h=0.247830, rho=−0.05, mu=1.464938). TR-specific handling: xG blend falls back to goals-only where absent; X3 is inactive before the xG era; no phase feature or mover adjustment was introduced.
