# Model design

## Feasibility

G-FEDA (goals) is buildable. S-FEDA, C-FEDA, K-FEDA, and T-FEDA are not buildable: no SOT, corners, Yellow-card, or total-shots target exists in the payloads, and there is no valid virgin target for those markets. Red and YellowRed events do not substitute for the absent Yellow target.

## G-FEDA

Reference: the production Dixon–Coles goals model as ported under `league/J1/engine/goals/`, using goals-only observations and `hl = 270`. The only arms are Gate Zero and the X2 newcomer-prior arm using the measured F4 magnitudes. There is no xG arm and no other rescue arm.

Warm-up is 2021. Scored development blocks are 2022–2025 (pooled n=2,083). The primary line is OU 2.5, whose development over-rate is 35.728%. The virgin definition is the 2026 group phase, n=459, with completeness established by inventory count only; no 2026 outcomes, rates, traits, or constants are used in Phase A.

Gate legs are dev versus league climatology and trailing-10; only an arm passing dev is read once on virgin. Virgin log loss must be no worse than Gate Zero and climatology, and calibration breach is <=1 percentage point for clean PASS, <=1 standard error for PROVISIONAL PASS, otherwise FAIL. No fitting, preregistration, predictions, or verdicts are part of Phase A.
