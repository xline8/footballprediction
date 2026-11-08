# C-DE3 verdict

Dev LL@10.5 (n=1,140):

| arm | pooled | 2022/23 | 2023/24 | 2024/25 | dev gate |
|---|---:|---:|---:|---:|---|
| Gate Zero (X9) | 0.686485 | 0.689326 | 0.696902 | 0.673226 | PASS |
| X7 | 0.685026 | 0.688967 | 0.692886 | 0.673226 | PASS |
| league base | 0.704277 | — | — | — | baseline |
| naive trailing-10 | 0.708042 | — | — | — | baseline |

Virgin (n=380; calibration is actual − predicted):

| arm | LL@10.5 | calibration | SE | 1pp+SE boundary | result |
|---|---:|---:|---:|---:|---|
| Gate Zero | 0.701771 | +3.273pp | 2.584pp | 3.584pp | PROVISIONAL PASS |
| X7 | 0.695904 | +3.288pp | 2.569pp | 3.569pp | PROVISIONAL PASS |
| best baseline (naive) | 0.724427 | — | — | — | baseline |

The exact calibration arithmetic is actual − predicted: GZ = 48.421% − 45.148% = +3.273pp; X7 = 48.421% − 45.133% = +3.288pp. Both arms meet the virgin LL legs and calibration within one SE; X7 also passes the dev per-season sign check (better than Gate Zero in at least 2 of 3 seasons). X7 has the lower virgin LL and ships. Prediction file: `predictions/c_de3_virgin_predictions.csv`.
