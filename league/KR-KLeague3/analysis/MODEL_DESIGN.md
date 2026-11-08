# Phase 6 — Model Design: KR-KLeague3 candidates

This is a design document only; no fitting is authorized here. The regular
played population is used, and 2021 playoffs remain frozen out.

| Candidate | Feasibility | Reason |
|---|---|---|
| G-KR3 goals | BUILDABLE | Goals are present for the 1,284 regular played matches. |
| S-KR3 SOT | NOT A CANDIDATE | Target absent in 0/1,296 payloads. |
| C-KR3 corners | NOT A CANDIDATE | Target absent in 0/1,296 payloads. |
| K-KR3 cards | NOT A CANDIDATE | Zero plain Yellow events; red-card events total 141 in 1,288 played matches (84 Red + 57 YellowRed, about 0.11 per match), and there is no 2.5 line. |
| T-KR3 total shots | NOT A CANDIDATE | Target absent in 0/1,296 payloads. |

## G-KR3 design

The reference is production goals-only Dixon–Coles, seeded from K2's G-KR2
engine. The two pre-registered arms are:

- **Gate Zero:** unmodified DC, rho grid `{0, -0.05, -0.10, -0.15}`,
  half-life 270 days, 14 IPF iterations, and prior 0.25.
- **SHRINK:** teams with fewer than six prior K3 matches shrink attack and
  defence toward the league mean.

There is no X2 arm. The primary line is OU 2.5. The scored dev over-rate is
0.4536 (2022–2024); the virgin 2025 over-rate is 0.4810.

The dev seed is 2021 (202 regular matches), with 2022–2024 scored (690
regular matches). The virgin is complete 2025 (210 regular matches), read
once and only for arms passing dev. The 2026 reserve is 182 played regular
matches, in progress, reserved and unread for confirmation.

The gate legs are identical to K2's `PREREG_G_KR2`: Gate Zero's pooled 1X2
log loss, RPS, and OU 2.5 log loss must all beat expanding climatology;
variants must beat climatology on all three and pass the per-season sign
check in at least two of the three scored dev seasons. The virgin gate and
calibration rule are `|breach| <= 1pp` clean, `<=1pp + 1SE` provisional,
otherwise fail. If both arms pass, select the lowest virgin 1X2 log loss;
ties prefer Gate Zero, then SHRINK.

Halves are presentation only: FT plus 1H/2H using frozen goals 1H share
0.4273. No SOT, corner, card, or total-shot model is designed.

