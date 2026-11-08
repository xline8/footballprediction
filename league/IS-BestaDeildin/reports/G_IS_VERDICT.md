# G-IS verdict — FAIL — virgin not read

Prereg: `prereg/PREREG_G_IS.md`. Dev pooled n=648. Virgin 2026 was **NOT read** because Gate Zero failed the dev gate; no arm ships.

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---:|---:|---:|
| Gate Zero | 1.017084 | 0.215499 | 0.669502 |
| SHRINK | 1.026100 | 0.218354 | 0.675039 |
| X2 | 1.031460 | 0.219616 | 0.675893 |
| Climatology | 1.052964 | 0.227613 | 0.655493 |

Gate arithmetic: Gate Zero passes 1X2 (1.017084 < 1.052964) and RPS (0.215499 < 0.227613), but fails OU2.5 (0.669502 > 0.655493). Variants are moot; the virgin was not read.

Phase B defect history: the X2 arm was initially dead because of split-year season labels. Coordinator verification caught the defect; it was fixed and re-run before the virgin stage. The dev numbers above are the corrected final numbers.

**Verdict: FAIL. Nothing ships.**
