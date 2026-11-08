# G-GR verdict

Preregistration: `prereg/PREREG_G_GR.md`; calibration is
actual − predicted. **Virgin NOT read** (dev gate failed).

## Dev (scored 2022/2023–2024/2025, n=716)

| arm / baseline | LL 1X2 | RPS | OU2.5 LL |
|---|---:|---:|---:|
| Gate Zero pooled | 0.969843 | 0.194787 | 0.716891 |
| SHRINK pooled | 0.969843 | 0.194787 | 0.716891 |
| climatology pooled | 1.080735 | 0.231077 | 0.700868 |

Per-season Gate Zero model OU2.5 LL vs climatology: 2022/2023
0.693271 vs 0.679778; 2023/2024 0.754513 vs 0.730621; 2024/2025
0.702653 vs 0.692060 — the model's OU2.5 is worse in **every**
dev season while its 1X2 LL beats climatology by ~0.11.

## Gate arithmetic

- Dev leg 1X2 LL: PASS (0.969843 < 1.080735).
- Dev leg RPS: PASS (0.194787 < 0.231077).
- Dev leg OU2.5 LL: **FAIL** — 0.716891 is not < base-rate
  0.700868. Gate Zero is dead; SHRINK is moot (and identical:
  SHRINK ≡ Gate Zero everywhere, the 1–5-match band never occurs
  under season-blocked fitting — the PL finding again).

G-GR verdict: **FAIL; nothing ships. Virgin deliberately NOT
read.** Prediction CSV: none. Fitted virgin params: none.
