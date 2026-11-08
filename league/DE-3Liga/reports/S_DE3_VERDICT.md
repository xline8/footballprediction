# S-DE3 verdict

Dev LL@9.5 (n=1,140):

| arm | pooled | 2022/23 | 2023/24 | 2024/25 | dev gate |
|---|---:|---:|---:|---:|---|
| Gate Zero | 0.686040 | 0.686266 | 0.688494 | 0.683360 | PASS |
| RS | 0.685449 | 0.685781 | 0.687385 | 0.683182 | PASS |
| league base | 0.690293 | — | — | — | baseline |
| naive trailing-10 | 0.694055 | — | — | — | baseline |

Virgin (n=380; calibration is actual − predicted):

| arm | LL@9.5 | actual rate | mean predicted | calibration | SE | result |
|---|---:|---:|---:|---:|---:|---|
| Gate Zero | 0.687909 | — | — | −4.321pp | 2.545pp | FAIL |
| RS | 0.686721 | — | — | −4.444pp | 2.542pp | FAIL |
| best baseline (naive) | 0.696521 | — | — | — | — | baseline |

The virgin actual over rate is 52.632%. The exact calibration arithmetic is actual − predicted: GZ = 52.632% − 56.953% = −4.321pp; RS = 52.632% − 57.076% = −4.444pp. Both arms beat Gate Zero/best-baseline LL, but neither satisfies the calibration leg: 4.321pp and 4.444pp exceed the 1pp limit even allowing one SE (3.545pp and 3.542pp). Both-pass is therefore empty. Nothing ships; no virgin prediction CSV is retained.
