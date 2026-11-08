# G-PL-ILiga verdict

Preregistration: `prereg/PREREG_G_PL-ILiga.md` (commit 4f9c42bc, before any
fitting). Calibration is actual − predicted. Virgin 2025/2026 was NOT
read for G-PL-ILiga: both arms failed the dev gate, and the prereg states
that if Gate Zero fails its own dev gate, variants are moot, verdict FAIL,
virgin NOT read.

## Dev

| arm / baseline | LL 1X2 | RPS | OU2.5 LL |
|---|---:|---:|---:|
| Gate Zero pooled | 1.092210 | 0.231355 | 0.701717 |
| SHRINK pooled | 1.092210 | 0.231355 | 0.701717 |
| climatology pooled | 1.087656 | 0.229661 | 0.695877 |

Per-season Gate Zero model LL (2022/23, 2023/24, 2024/25) is 1.107575,
1.091625, 1.077429; climatology is 1.090433, 1.081518, 1.091018. The model
beats climatology only in 2024/2025. SHRINK is identical in every season:
the shrinkage adjustment changed 0 of 918 scored lambdas (the 1–5
prior-match band never occurs under season-blocked fitting, as in PL).

## Gate arithmetic

- Dev gate, Gate Zero: **FAIL** — pooled 1X2 LL 1.092210 is worse than
  climatology 1.087656 (by 0.004554); RPS 0.231355 is worse than 0.229661
  (by 0.001694); OU2.5 LL 0.701717 is worse than the base-rate 0.695877
  (by 0.005840). All three legs fail, so the arm is dead at dev.
- Dev gate, SHRINK: **FAIL** for the same numbers (identical results).

G-PL-ILiga verdict: **FAIL (dev gate); nothing ships**. No virgin read,
no predictions CSV, no fitted virgin params, no `results_virgin.json`.

Verification: coordinator recomputed the pooled climatology numbers
independently from the CSV (LL 1.087656, RPS 0.229661, OU 0.695877 — exact
to 6 decimals); `dc.py`/`arms.py` are byte-identical to the PL engine;
the harness differs only by the regular-phase filter and its assertions;
a re-run of the dev runner reproduces `results_dev.json` exactly; zero
xG values were consumed (the feed is absent in every row).

Note: the goals-for trait is reliable (split-half r = 0.721) yet the
unmodified DC pattern still loses to climatology on this dev window —
the goals-against trait is weak (r = 0.281) and the league turns over
6 of 18 clubs every season. The FAIL is recorded plainly; no rescue arm
was invented.
