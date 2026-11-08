# G-PT Verdict — Liga Portugal goals model

Date: 2026-11-09. Branch `build/pt-liga`. Prereg:
`league/PT-LigaPortugal/prereg/PREREG_G_PT.md` (commit dc457f5,
frozen before any fitting). Engine: `league/PT-LigaPortugal/engine/goals/`.

## Verdict: FAIL — nothing ships

Gate Zero passes the dev gate and the virgin LL leg, and its
home-win calibration is a provisional pass, but the virgin OU2.5
calibration breach (−5.58pp) exceeds 1 SE (5.01pp) — the same leg
that killed G-J1. The transitional virgin season ran away-hot
(39.8% away wins, over-2.5 rate 53.1% vs 47.5% predicted); the gate
is mechanical and is applied as written. A season-end confirmatory
read of 2026/2027 is reserved by the prereg frame.

## Dev results (expanding season-blocked, pooled n=1,224)

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | 0.9355 | 0.1868 | 0.6822 |
| SHRINK | 0.9355 | 0.1868 | 0.6822 |
| Climatology | 1.0728 | 0.2328 | 0.6940 |

Per-season Gate Zero 1X2 LL: 0.9025 / 0.9416 / 0.9671 / 0.9306.
Dev gate: PASS for both arms. SHRINK is a documented no-op in this
design: season-blocked training counts are 0 (unseen — rating is
already the league mean, scaling changes nothing) or ≥34, so no
team ever meets the <15-match condition. The defect is in the arm's
interaction with season-blocked fitting, recorded here; fixing it
would need a new prereg (e.g. a within-season walk-forward).

## Virgin results (2026/2027, transitional, n=98, read once)

| Arm | 1X2 LL | Home-win calib | OU2.5 calib |
|---|---|---|---|
| Gate Zero / SHRINK (identical) | 0.9120 | +3.54pp (SE 4.30) | −5.58pp (SE 5.01) |
| Climatology | 1.0721 | — | — |

Legs (Gate Zero): (i) LL 0.9120 ≤ climatology 1.0721 PASS;
(ii) home-win PROVISIONAL PASS (breach ≤ 1 SE), OU2.5 FAIL
(5.58 > 5.01) → leg FAIL; (iii) n/a (comparator). SHRINK inherits
the identical numbers and the tie rule would have shipped Gate
Zero had both passed. **Overall: FAIL.**

## Verification notes

- The engine's dev numbers were reproduced by replaying the
  2022/2023 fit through J1's own production-pattern DC code
  (`league/J1/engine/goals/dc.py`): 1X2 LL 0.9025483335494278 vs
  the engine's 0.9025483335494274.
- Two coordinator fixes to Codex's first version, before dev
  froze: RPS was computed as a Brier sum (now the prereg's
  cumulative formula; pooled RPS 0.1868), and SHRINK was applied
  inside the fit (now applied after the fit, per prereg).
- Virgin predictions on file are Gate Zero's, labelled as such
  (`predictions/g_pt_virgin_predictions.csv`), per the prereg's
  output rule for a FAIL.
