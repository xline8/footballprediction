# G-PL verdict

Preregistration: `prereg/PREREG_G_PL.md`; virgin is 2025/2026, n=306, read once. Calibration below is actual − predicted.

## Dev

| arm / baseline | LL 1X2 | RPS | OU2.5 LL |
|---|---:|---:|---:|
| Gate Zero pooled | 1.060899 | 0.220611 | 0.689337 |
| SHRINK pooled | 1.060899 | 0.220611 | 0.689337 |
| climatology pooled | 1.077230 | 0.226433 | 0.693207 |

Both arms pass all three dev legs. Per-season Gate Zero model LL (2022/23, 2023/24, 2024/25) is 1.060005, 1.094617, 1.028076; SHRINK is identical.

## Virgin table

| arm / baseline | LL 1X2 | RPS | OU2.5 LL | home-win cal pp ± SE | OU2.5 cal pp ± SE |
|---|---:|---:|---:|---:|---:|
| Gate Zero | 1.074664 | 0.221879 | 0.693356 | +0.915 ± 2.842 | +2.137 ± 2.860 |
| SHRINK | 1.074664 | 0.221879 | 0.693356 | +0.915 ± 2.842 | +2.137 ± 2.860 |
| climatology | 1.069744 | 0.222918 | 0.695205 | +1.471 ± 2.849 | +3.758 ± 2.861 |

## Gate arithmetic

- Gate Zero leg (i): **FAIL** — 1.074664 is not ≤ climatology 1.069744.
- Gate Zero leg (ii): home-win +0.915 pp is a **clean PASS** (inside the 1.0 pp boundary); OU2.5 +2.137 pp breaches the boundary by 1.137 pp, within 1 SE (2.860 pp), so **PROVISIONAL PASS** on that sub-leg.
- Gate Zero leg (iii): exempt.
- SHRINK leg (i): **FAIL** for the same tie result; leg (ii) is the same provisional result; leg (iii) is a dev tie in all three seasons and therefore goes to Gate Zero.

Both fail the virgin LL leg. G-PL verdict: **FAIL; nothing ships**. SHRINK ≡ Gate Zero in virgin too: the 1–5-match band never occurs under season-blocked fitting.

Prediction CSV: none. Fitted virgin params: none. Verification: coordinator cross-checked results_virgin.json (LL 1X2 1.074664 vs climatology 1.069744; calibration diffs +0.915/+2.137 pp with SEs 2.842/2.860) — the FAIL rests on leg (i) alone.
