# HU-NBI model design (pre-fit freeze)

This document and `prereg/PREREG.md` freeze the design before any fitting. Phase A performs no model fitting, walk-forward scoring, or LL calculation.

Windows are expanding walk-forward by season: development targets are 2022/2023, 2023/2024, and 2024/2025, with all prior seasons available to each fit; virgin is 2025/2026 (198 complete matches). 2026/2027 is reserved and never read beyond inventory. Stat markets use available target rows; the six missing stats rows are not fabricated and do not make a window unusable.

Candidates and Gate Zero patterns:

| candidate | target | primary line | Gate Zero | registered variants |
|---|---|---:|---|---|
| G-HU-NBI | match goals | 2.5 | goals-only Dixon–Coles production pattern | thin-team shrinkage/prior arm |
| S-HU-NBI | SOT | 8.5 | `model_sot.py` v5 pattern | ratio-shrink arm |
| C-HU-NBI | corners | 9.5 | `model_corners_v3.py`, possession-only covariate | plain/no-multiplier ablation |
| K-HU-NBI | event-unified yellows | 4.5 | `model_cards.py` pattern | none; referee dropped |
| T-HU-NBI | total shots | 19.5 | J1 shots family arm A v1 | arms B/C only under the preregistered J1 design |

Primary lines are the nearest .5 line to the pooled development mean: 2.8384 goals, 8.5646 SOT, 10.0136 corners, 4.5825 cards, and 19.0425 total shots.

Goals and event cards may be presented as FT plus 1H/2H using frozen constants. SOT, corners, and total shots are FT-only because no period splits or event-level sources exist.
