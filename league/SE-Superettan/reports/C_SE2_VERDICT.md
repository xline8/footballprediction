# Verdict — C-SE2 (SE-Superettan corners): **FAIL (virgin leg ii, calibration)**

Frozen gates: PREREG_C_SE2.md (730a5c1, before fitting). Primary line 10.5.
Single arm (X7 impossible: no touches key in the feed). Gate Zero's territorial
multiplier is possession-only (feed-forced, frozen in the prereg); the fitted
possession beta is **0.0** in the virgin fit, as in most program leagues — the
multiplier is inert and Gate Zero ships-or-fails in its plain form.

## Dev (warm-up 2022; scored 2023–2025, n = 710)
Gate Zero LL@10.5 **0.699415** vs league base rate 0.708632, naive 0.710150 → dev gate PASS.

## Virgin 2026 (n = 237) — read ONCE (see defect note)
| | LL@10.5 | mean P(over) | actual |
|---|---|---|---|
| Gate Zero | 0.700234 | 0.3894 | 0.4557 |
| League base rate | 0.717050 | | |
| Naive trailing-10 | 0.711933 | | |

Leg (i) PASS (0.700234 ≤ both baselines). Leg (ii): calibration diff
**−6.63pp**, 1 SE = 3.25pp → breach beyond 1pp + 1 SE (4.25pp). **FAIL.**
The virgin ran corner-hot relative to the model's level (actual over-rate
0.4557 vs dev-era ~0.46 at this line, but the model's probabilities sat low).
Nothing ships.

## Defect found and corrected BEFORE the virgin read counted
The corners harness's virgin path still targeted season "2025" (SE's virgin,
missed in adaptation). A first run therefore produced metrics on the DEV
season 2025 (n = 239; LL@10.5 0.678412, calibration +5.31pp) mislabelled as a
virgin read. That read touched only already-seen dev data — the true virgin
(2026) was still unread. The harness was corrected (target season 2026) and
the real virgin was then read once; the numbers above are that read. The
mislabelled run is recorded here for transparency, not used anywhere.
