# Model design — Wales Cymru Premier

## Feasibility

| candidate | dev target | virgin target | status |
|---|---:|---:|---|
| G-WAL goals | scores exist, 1,087 eligible (576 scored eval rows + 192 seed) | 192/192 eligible | BUILD |
| S-WAL SOT | 0/1,087 | 0/192 | NOT BUILDABLE |
| C-WAL corners | 0/1,087 | 0/192 | NOT BUILDABLE |
| K-WAL cards | 0/1,087 (no yellow target; 234 dismissals only) | 0/192 | NOT BUILDABLE |
| T-WAL total shots | 0/1,087 | 0/192 | NOT BUILDABLE |

G-WAL is production DC Gate Zero (`model_v2.py` pattern): half-life 270, rho grid, MAXG=10, goals-only. The only arm is SHRINK: when prior in-league n<6, `a*=a*n/6`, `d*=d*n/6`; dev and virgin have no 1–5 prior teams, so changed_rows must still be reported and is 0. Fit pools regular and split rows with phase only; playoffs are excluded.

Dev seed is 2021/2022; evaluate 2022/2023–2024/2025, pooled scored n=576. Virgin primary is 2025/2026, n=192, read once only if Gate Zero passes dev. Confirmatory 2026/2027 is reserved, not part of this build. Primary line is OU 2.5. Gates: dev pooled 1X2 LL + RPS beat climatology and OU2.5 LL beats base rate; virgin (i) LL ≤ Gate Zero and climatology, (ii) calibration `actual−predicted` within 1pp with ≤1 SE provisional, and (iii) dev fold sign check. Calibration is actual minus predicted everywhere.
