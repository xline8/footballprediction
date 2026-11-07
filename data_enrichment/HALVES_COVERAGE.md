# SOT halves dataset — coverage report

Combined historical shots-on-target half splits for the top-5 leagues, built on the football-data spine (`all_matches_clean.csv`, full-time SOT = HST+AST). Source A: the SofaScore dataset already in this repo. Source B: FotMob shotmaps via `data_enrichment/fill_halves_gaps.py`, used only where SofaScore has no split. Per-row provenance is in the `source` column of `sot_halves_combined.csv`.

- Spine matches (top-5, 2017/18 onward, with FT SOT): **16560**
- Matches with half splits: **15633 (94.4%)**
- By source: fotmob 2472, sofascore 13161
- Still missing: **927** (see 'Remaining gaps')

## Coverage by division x season (halves / spine)

| Div | 2017/18 | 2018/19 | 2019/20 | 2020/21 | 2021/22 | 2022/23 | 2023/24 | 2024/25 | 2025/26 | 2026/27 | Total |
|---|---|---|---|---|---|---|---|---|---|---|---|
| E0 | 366/380 | 380/380 | 380/380 | 380/380 | 379/379 | 380/380 | 380/380 | 380/380 | 380/380 | 90/90 | 3495/3509 |
| SP1 | 306/380 | 342/380 | 342/380 | 380/380 | 380/380 | 380/380 | 380/380 | 380/380 | 380/380 | 109/109 | 3379/3529 |
| D1 | 304/306 | 306/306 | 306/306 | 306/306 | 306/306 | 306/306 | 306/306 | 305/305 | 306/306 | 72/72 | 2823/2825 |
| I1 | 380/380 | 380/380 | 380/380 | 380/380 | 380/380 | 380/380 | 380/380 | 380/380 | 380/380 | 99/99 | 3519/3519 |
| F1 | 273/380 | 3/380 | 4/279 | 379/380 | 380/380 | 380/380 | 305/306 | 306/306 | 306/306 | 81/81 | 2417/3178 |
| **All** | 1629/1826 | 1411/1826 | 1412/1725 | 1825/1826 | 1825/1825 | 1826/1826 | 1751/1752 | 1751/1751 | 1752/1752 | 451/451 | 15633/16560 |

## Cross-validation: FotMob vs SofaScore (seeded sample)

The FotMob filler also labelled 130 matches that already had SofaScore splits, out of a seeded random sample of 200 SofaScore-covered matches (seed 20261107); the other 70 sample matches hit the same FotMob no-shotmap depth limit described under 'Remaining gaps' and could not be labelled by FotMob at all. Agreement on the 130 matches both sources cover:

| Field | Exact | Exact % | MAE |
|---|---|---|---|
| 1H home | 130/130 | 100.0% | 0.0 |
| 1H away | 130/130 | 100.0% | 0.0 |
| 2H home | 129/130 | 99.2% | 0.008 |
| 2H away | 130/130 | 100.0% | 0.0 |
| All four splits exact | 129/130 | 99.2% | — |
| Full-time total exact | 129/130 | 99.2% | — |

## Sanity checks

- Halves sum vs football-data FT total: exact in 85.78% of combined rows. Delta distribution (halves − FT): -12: 2, -11: 2, -8: 3, -7: 10, -6: 13, -5: 40, -4: 88, -3: 186, -2: 368, -1: 953, 0: 13410, 1: 496, 2: 46, 3: 11, 4: 4, 6: 1. Split by source, the picture differs: FotMob rows are exact in 94.7% and within ±1 in 99.4% (one row with |delta| ≥ 4), while SofaScore rows are exact in 84.1% and within ±1 in 94.2%, and their |delta| ≥ 4 tail (162 rows, mostly 2018/19–2020/21) sits almost entirely in rows SofaScore itself marked quarantine (139) or flagged (23). Small ±1 deltas are a counting-definition difference between providers. Where both sources have splits they agree almost perfectly (cross-validation below), so the SofaScore-first priority costs little; the quarantined SofaScore rows are the least trustworthy rows in the file.
- SofaScore internal consistency: 1H+2H sums disagree with SofaScore's own FT total in 24 of 13161 top-5 rows.
- Rows where both teams' 1H SOT = 0: 65 FotMob-sourced, 310 SofaScore-sourced. For FotMob rows this pattern can indicate silently missing 1H shotmap data; the count is reported here rather than the rows being silently trusted. (Where the halves still sum to the FT total, a genuine goalless-on-target first half is plausible.)

## Remaining gaps

927 spine matches have no half split from either source. These are the matches to target with the Chrome DevTools SofaScore scraper on the user's machine. The full per-match list with reasons is in `data_enrichment/sot_backfill/remaining_gaps.csv`.

By division x season (missing count):

| Div | 2017/18 | 2018/19 | 2019/20 | 2020/21 | 2021/22 | 2022/23 | 2023/24 | 2024/25 | 2025/26 | 2026/27 | Total |
|---|---|---|---|---|---|---|---|---|---|---|---|
| E0 | 14 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 14 |
| SP1 | 74 | 38 | 38 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 150 |
| D1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 |
| I1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| F1 | 107 | 377 | 275 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 761 |

Reasons (from the FotMob fill run):

- fetch/extract failed: ValueError('stats payload has no half split'): 927

