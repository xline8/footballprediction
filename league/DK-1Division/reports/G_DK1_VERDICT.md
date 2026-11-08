# G-DK1 verdict — FAIL (virgin deliberately UNREAD)

Dev (season-blocked walk-forward, seed 2021/2022, scored 2022/2023–2024/2025,
pooled n=576), vs pooled-prior climatology:

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---:|---:|---:|
| Gate Zero | 1.0809 | 0.2373 | 0.7108 |
| SHRINK | 1.0809 | 0.2373 | 0.7108 |
| X2 mover | 1.1367 | 0.2554 | 0.7084 |
| Climatology | 1.0738 | 0.2369 | 0.6877 |

Gate arithmetic: the dev gate requires Gate Zero to beat climatology on
1X2 LL, RPS and OU2.5 LL. It beats none (1.0809 > 1.0738; 0.2373 >
0.2369; 0.7108 > 0.6877). Gate Zero FAILS dev ⇒ variants are moot and
the 2025/2026 virgin was NOT read (results_virgin.json records this).

Notes: SHRINK is numerically identical to Gate Zero on the scored dev
seasons (0 of 576 predictions differ) — by the first scored season every
returning team already has ≥6 training matches and newcomers have 0,
where the two rules coincide; the arm never bites in this window. X2
was genuinely implemented (9–12 mover teams blended per season from a
DC fit on the parent DK-Superligaen's preceding season; 124 of 576
predictions differ) and was clearly worse (1X2 LL 1.1367). Nothing
ships. All headline numbers independently recomputed by the
coordinator from dev_predictions.csv.
