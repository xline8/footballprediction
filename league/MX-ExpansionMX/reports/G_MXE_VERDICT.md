# Verdict — G-MXE (Liga de Expansión MX goals) — **FAIL (virgin LL leg + home-win calibration leg)**

Prereg: `prereg/PREREG_G_MXE.md` (frozen before any fitting).
Population: finished + regular only (liguilla excluded).
Dev = tournament-blocked walk-forward, seed 2021/2022 - Apertura
(n=136), scored blocks 2–9 (n=967). Virgin = 2025/2026 - Clausura
(n=105), read once because Gate Zero passed the dev gate.
All headline numbers were recomputed independently via the
production `model_v2.DC` (second code path) and match the engine
to 4 decimals.

## Dev results (pooled, n=967)

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Climatology (baseline) | 1.0631 | 0.2218 | 0.6958 |
| Gate Zero | **1.0420** | **0.2145** | **0.6930** |
| SHRINK | 1.0420 | 0.2145 | 0.6930 |

Gate Zero beats climatology on all three dev metrics → dev gate
PASS. Per-block 1X2 LL: Gate Zero beats climatology in 7 of 8
blocks (loses only the first scored block, 2021/2022 - Clausura:
1.1639 vs 1.0767). **SHRINK never bites** — 0 of 967 dev
predictions differ from Gate Zero: under tournament-blocked
fitting every entrant has exactly 0 prior in-league matches at its
first block (where SHRINK coincides with the unseen rule) and every
incumbent has ≥136. Same structural finding as CL-LigaDeAscenso.

## Virgin results (n=105, read once)

| Arm | 1X2 LL | RPS | OU2.5 LL | HW calib | OU calib |
|---|---|---|---|---|---|
| Climatology | **1.0131** | **0.2033** | **0.6951** | +9.27pp | +6.10pp |
| Gate Zero / SHRINK | 1.0719 | 0.2211 | 0.7114 | +7.85pp (SE 5.00) | +2.15pp (SE 4.97) |

## Gate arithmetic (mechanical, per the frozen prereg)

- (i) LL leg: 1.0719 > climatology 1.0131 → **FAIL**. The virgin
  block was a strong-home block (actual home-win rate 55.2% vs
  the dev pooled 47.1%); the model's decayed ratings, fitted
  through a weak-home stretch, under-called home wins by more
  than the flat climatology did.
- (ii) Calibration leg: home-win breach +7.85pp with SE 5.00pp —
  the provisional boundary is 1.0 + 5.00 = 6.00pp; 7.85 > 6.00 →
  home-win calibration **FAIL**. OU2.5 breach +2.15pp is within
  its provisional boundary (1.0 + 4.97 = 5.97pp) → PROVISIONAL on
  the OU sub-leg, but the calibration leg as a whole fails on
  home-win.
- (iii) Sign leg: satisfied but moot (both other legs failed).

## What ships

Nothing. No fitted params, no predictions CSV. G-MXE = FAIL.
The engine, dev/virgin results and this verdict are the complete
record. The 2026/2027 confirmatory window was never read.
