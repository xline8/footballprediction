# T-DE3 verdict

Dev LL@26.5 (n=1,140):

| arm | pooled | 2022/23 | 2023/24 | 2024/25 | dev gate |
|---|---:|---:|---:|---:|---|
| A | 0.672092 | 0.672807 | 0.684535 | 0.658934 | PASS |
| B | 0.671767 | 0.672224 | 0.685257 | 0.657821 | PASS |
| C | 0.672370 | 0.673458 | 0.684274 | 0.659377 | PASS |
| league base | 0.694647 | — | — | — | baseline |
| naive trailing-10 | 0.679220 | — | — | — | baseline |

Virgin (n=380; calibration is actual − predicted):

| arm | LL@26.5 | calibration | SE | 1pp+SE boundary | result |
|---|---:|---:|---:|---:|---|
| A | 0.687426 | +2.691pp | 2.546pp | 3.546pp | PROVISIONAL PASS |
| B | 0.689767 | +1.942pp | 2.553pp | 3.553pp | FAIL (LL) |
| C | 0.687216 | +3.159pp | 2.544pp | 3.544pp | FAIL (dev sign) |
| best baseline (league) | 0.688272 | — | — | — | baseline |

The exact calibration arithmetic is actual − predicted: A = 55.789% − 53.098% = +2.691pp; B = 55.789% − 53.847% = +1.942pp; C = 55.789% − 52.631% = +3.159pp. A is the frozen reference arm because it passes dev. A meets the virgin LL, calibration, and sign legs within one SE and ships. C has the slightly lower raw virgin LL but does not satisfy the required per-season sign check against A; B fails the virgin LL leg. Prediction file: `predictions/t_de3_virgin_predictions.csv`.
