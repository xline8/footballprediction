# Model design — IS-BestaDeildin Phase A

This freezes the later evaluation design; Phase A does not implement or fit
any engine. Training seed is 2021. Goals dev is 2022–2025 (648 rows) and
virgin is 2026 (162 rows). Stats warm-up is 2023, scored stats dev is
2024–2025 (324 rows), and stats virgin is 2026 (162 rows). Dev harnesses must
not read 2026.

G-IS uses the HR Dixon–Coles goals-only Gate Zero, SHRINK, and the in-corpus
X2 entrant arm, with HR rho grid and 270-day decay. Primary legs are OU2.5
log loss plus 1X2 log loss/RPS as in PREREG_G_HR.

S-IS uses Gate Zero v5 and RS with beta-binomial prior 200→20,000 (primary
9.5; ladder 8.5/9.5/10.5). C-IS uses corners_v3 with full X9
possession+big_chance and X7 box touches under the 2024+ restriction (primary
11.5; ladder 10.5/11.5/12.5). K-IS uses the cards family and X8 referee
multiplier with stats yellow_cards (primary 4.5; ladder 3.5/4.5/5.5). T-IS
uses A, B and C/E9 trailing-200-r (primary 27.5; ladder 26.5/27.5/28.5).

Every gate uses the frozen HR text: dev over-rate is computed from the CSV;
calibration is clean at |breach|≤1pp, provisional within one SE, otherwise
FAIL. Both-pass/tie rules apply, and Gate Zero dev failure makes variants moot
and prevents reading virgin rows. No model fitting is performed in Phase A.
