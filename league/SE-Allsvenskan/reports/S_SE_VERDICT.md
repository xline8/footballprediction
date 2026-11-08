# S-SE verdict — PROVISIONAL PASS (arm X4 ships)

Prereg: `league/SE-Allsvenskan/prereg/PREREG_S_SE.md` (frozen in
commit 62320f5, before any fitting). Primary line 8.5. Dev =
per-match walk-forward, scored seasons 2022–2024 (n = 720);
virgin = 2025 (n = 240), read once.

## Dev results (pooled LL@8.5)

| Arm / baseline | LL@8.5 | Per-season sign vs GZ |
|---|---|---|
| Gate Zero | 0.6747 | — |
| RS | 0.6762 | 1/3 |
| X4 | 0.6756 | 2/3 |
| League base rate | 0.6915 | |
| Naive trailing-10 | 0.6879 | |

All three arms beat both baselines on pooled dev LL. RS fails the
leg-(iii) sign check (its dev LL ≤ Gate Zero's in only 1 of 3
seasons); the harness (the DK/NL-shared mechanical reading) applies
the sign check as a pre-filter, so **RS was not virgin-read** — it
cannot pass, and that is recorded here plainly rather than hidden.

## Virgin results (2025, n = 240; actual over-8.5 rate 0.5333)

| Arm | LL@8.5 | Calibration (mean P − actual) | SE |
|---|---|---|---|
| Gate Zero | 0.6707 | −2.92pp | 3.16pp |
| X4 | 0.6703 | −3.37pp | 3.15pp |
| League base rate | 0.6909 | −0.21pp | |
| Naive trailing-10 | 0.6736 | −3.70pp | |

## Gate arithmetic

- Dev gate: GZ, RS, X4 all pass (above).
- Virgin leg (i): GZ 0.6707 ≤ best baseline 0.6736 ✓; X4 0.6703 ≤
  Gate Zero ✓ and ≤ best baseline ✓.
- Virgin leg (ii): both arms breach the 1.0pp calibration boundary
  (GZ −2.92pp, X4 −3.37pp) but each breach is within 1 SE of the
  boundary (1.0 + 3.16 = 4.16pp; 1.0 + 3.15 = 4.15pp) →
  **PROVISIONAL PASS** for both.
- Leg (iii): X4 2/3 ✓; RS 1/3 ✗ (not read, cannot ship).
- Both-pass rule: GZ and X4 both pass (provisionally); the lower
  pooled virgin LL ships → **X4 (0.6703 < 0.6707)**.

**Verdict: PROVISIONAL PASS. Arm X4 ships** — v5 pattern with the
BB on-target ratio replaced by the xG/shot quality input (the weak
F6 trait, r = 0.268, earned its place through the gate, narrowly).
Predictions: `predictions/s_se_virgin_predictions.csv` (240 rows;
FT ladder 7.5/8.5/9.5; 1H/2H presentation-only via the frozen SOT
constant 0.455). Fitted params: `engine/sot/fitted_params_virgin.json`
(arm X4). Independent recomputation of the virgin LL@8.5 from the
predictions CSV reproduces 0.670304 exactly. Predictions-only
product: no SE SOT odds/settlement source in-system.
