# Phase 3.5 — Feature Engineering: GR-SuperLeague X1–X9

The global causality contract is unchanged: a target match may use
only strictly earlier matches; windows are trailing; ratios are
ratios of sums; missing windows make an arm inactive. Ratings, home
advantage, Dixon–Coles parameters, count distributions, and halves
constants are architecture or presentation components, not
covariates. All reliabilities are the GR measurements in EDA.md.

| ID | Feature | GR verdict | Evidence and use |
|---|---|---|---|
| X1 | Goals plus stats-feed xG blend | ADOPTED with era guard | Goals exist for all 1,261 rows. Stats xG is full only from 2025/2026 (12 + 6 stray matches before), so the blend runs goals-only almost everywhere in dev and in the virgin fit; xG reliability (0.830) is measured inside the virgin era and supports no separate arm. Production blend pattern with goals-only fallback, unchanged. |
| X2 | Mover tier offset | MEASURED, NOT CONSUMED | 9 newcomers, 1–2 per transition: GF gap −0.157, GA gap +0.283 vs the pooled league team mean. Super League 2 (8815) exists in the warehouse but contains non-promotable B teams and no SL2 corpus is built, so no true tier offset is estimated; SHRINK is the goals thin-data arm (PL/BE precedent). |
| X3 | Set-play xG share/rate | DROPPED | Set-play share reliability 0.193 and rate reliability 0.165 — both fail reliability outright; coverage also starts inside the virgin. Dead on two legs. |
| X4 | Shotmap xG per shot | DROPPED (era) | Reliability is real (0.665) but the shotmap era is 2025/2026–2026/2027 only, with 12 + 6 stray matches before: an era starting inside the virgin kills the arm (ES lesson). |
| X5 | Trailing target means | ADOPTED | SOT, corners, and unified yellows are available as target histories in every season (yellows via events in 2021/2022). Reliability: SOT 0.850/0.808, corners 0.833/0.714, yellows 0.686/0.488 — the strongest X5 base in the programme. |
| X6 | Attacking xGOT per shot | DROPPED | Era-guarded reliability 0.264, below the ~0.35 arm standard; era is 2025+ only, which would kill it anyway. |
| X7 | Opp-box touches | ADOPTED conditionally | For/against reliability 0.953/0.855 — the strongest territorial trait measured in the programme. Coverage 0.0% in 2021/2022, 82.5% / 89.6% in the next two seasons, ~100% from 2024/2025; the min-8 trailing-window rule controls availability. |
| X8 | Referee yellow rate | DROPPED | Reliability 0.262 over the 15 referees meeting the sample threshold (117 distinct referees named — heavy foreign-referee rotation); a random re-split gives −0.07. Below every adopted referee trait in the programme (BE 0.378 is the lowest). Coverage also 0.0% in the seed season and 73.7% in 2024/2025. K-GR runs Gate Zero only. |
| X9 | Possession and big chances for corners | ADOPTED as Gate Zero reference | Possession reliability 0.931 and big-chance reliability 0.860. They remain the reference territorial covariates; X7 is tested as the additional arm. |

Rejected inherited items remain rejected: team half shares are
presentation constants (goals/shots true variance ~0; corners
0.0053 is the programme's largest and still constant-only by rule);
finishing and standalone conversion are outcome-contaminated;
on-target rate reliability is 0.083 (noise); defensive xGOT is not
eligible; lineup, formation, coach, standings, h2h, attendance,
game-state, momentum, and red-card features have no admissible
pre-match evidence here.

## Consumption map

- G-GR: X1 (blend with goals-only fallback); SHRINK is the thin-data
  arm; X2 measured but not consumed; X3 not run.
- S-GR: X5; RS ratio-shrink arm per the reference architecture;
  X4 and X6 rejected.
- C-GR: X5 and X9 Gate Zero; X7 conditional arm.
- K-GR: X5 only; Gate Zero only (X8 dropped).
- T-GR: arms A/B/C of the shots family; no new feature arm.
