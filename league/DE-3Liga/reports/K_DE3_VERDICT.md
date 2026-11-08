# K-DE3 verdict

Dev LL@4.5 (n=1,140):

| arm | pooled | 2022/23 | 2023/24 | 2024/25 | dev gate |
|---|---:|---:|---:|---:|---|
| Gate Zero | 0.690122 | 0.700728 | 0.706910 | 0.662729 | PASS |
| X8 | 0.687332 | 0.701194 | 0.694384 | 0.666418 | PASS |
| league base | 0.693426 | — | — | — | baseline |
| naive trailing-10 | 0.699551 | — | — | — | baseline |

Virgin (n=380; calibration is actual − predicted):

| arm | LL@4.5 | calibration | SE | 1pp+SE boundary | result |
|---|---:|---:|---:|---:|---|
| Gate Zero | 0.690177 | −2.734pp | 2.557pp | 3.557pp | FAIL |
| X8 | 0.680674 | −3.512pp | 2.530pp | 3.530pp | FAIL |
| best baseline (naive) | 0.668168 | — | — | — | baseline |

The exact calibration arithmetic is actual − predicted: GZ = 53.158% − 55.892% = −2.734pp; X8 = 53.158% − 56.669% = −3.512pp. Neither arm beats the best virgin baseline on LL, and the frozen calibration rule fails both arms (X8 is just beyond the one-SE boundary). Nothing ships; no virgin prediction CSV is retained.
