# Model SOT v6 — Per Babak + Kondisi Skor Turun Minum (eksperimen, BUKAN produksi)

## Ringkasan (Bahasa Indonesia)

Pertanyaan: apakah menghitung tembakan ke gawang per babak (babak 1 dan babak 2 dinilai terpisah dari dataset gabungan SofaScore+FotMob), dengan perkiraan babak 2 disyaratkan pada keadaan skor saat turun minum (unggul / imbang / tertinggal), mengalahkan resep produksi v5 pada uji walk-forward yang sama?

Jawaban: **TIDAK — tidak lolos gerbang**. Pada 5,255 laga uji lima liga top (2023/24–2025/26), log loss garis 9,5: v5 = 0.6488, varian babak = 0.6502 (selisih +0.0014); kesalahan kalibrasi: v5 = 0.0pp, varian babak = 0.6pp; divisi paling memburuk: +0.0023 (batas +0,003). Pengali keadaan turun minum dari data pemanasan: tertinggal ×1.049, imbang ×0.978, unggul ×0.964 — arahnya sesuai dugaan (tim tertinggal menembak lebih banyak di babak 2), besarnya kecil.

Produksi TIDAK diubah oleh eksperimen ini apa pun hasilnya — keputusan adopsi ada di tangan user setelah membaca laporan ini.

## Reference reproduction check

Production v5 (slim+R+NB+BB) recomputed in this pass over ALL divisions: pooled line-9.5 log loss **0.6304** (RESULTS_V5.md: 0.6304) → **MATCH**. n = 21,461. Frozen choices re-derived from warm-up only: ridge lambda = 100, BB prior = 200, NB r = 79.94.

## HT-state multipliers (frozen from 2019/20–2022/23)

| State (team's own view) | Team-matches | Σ predicted 2H | Σ actual 2H | Multiplier |
|---|---|---|---|---|
| lead | 4,142 | 10334 | 9964 | 0.964 |
| level | 5,492 | 12889 | 12603 | 0.978 |
| trail | 4,142 | 9334 | 9791 | 1.049 |

## Headline — top-5 test matches, line 9.5

| Variant | LogLoss | Brier | Calib err (pp) | MAE | ΔLL vs v5 |
|---|---|---|---|---|---|
| v5 (production) | 0.6488 | 0.2285 | 0.0 | 2.44 | +0.0000 |
| v5 without BB (ablation baseline) | 0.6488 | 0.2285 | 0.0 | 2.44 | -0.0000 |
| halves (per-half + HT state) | 0.6502 | 0.2292 | 0.6 | 2.42 | +0.0014 |

## All lines — top-5 pooled log loss

| Variant | 7.5 | 8.5 | 9.5 | 10.5 |
|---|---|---|---|---|
| v5 | 0.6311 | 0.6710 | 0.6488 | 0.5694 |
| v5-nobb | 0.6309 | 0.6709 | 0.6488 | 0.5693 |
| halves | 0.6328 | 0.6728 | 0.6502 | 0.5703 |

## By division — line 9.5 log loss (top-5 test matches)

| Div | n | v5 | halves | Δ |
|---|---|---|---|---|
| E0 | 1,140 | 0.6648 | 0.6666 | +0.0019 |
| D1 | 917 | 0.6780 | 0.6803 | +0.0023 |
| I1 | 1,140 | 0.6098 | 0.6090 | -0.0008 |
| SP1 | 1,140 | 0.6314 | 0.6336 | +0.0022 |
| F1 | 918 | 0.6697 | 0.6716 | +0.0019 |

## By season — line 9.5 log loss (top-5)

| Season | n | v5 | halves | Δ |
|---|---|---|---|---|
| 2023/24 | 1,752 | 0.6545 | 0.6568 | +0.0022 |
| 2024/25 | 1,751 | 0.6470 | 0.6477 | +0.0007 |
| 2025/26 | 1,752 | 0.6449 | 0.6463 | +0.0013 |

## Gate verdict

- Pooled (top-5) log loss improves: **NO** (0.6502 vs 0.6488).
- Calibration does not worsen: **NO** (0.6pp vs 0.0pp).
- No top-5 division worsens by >0.003: **YES** (worst +0.0023).
- **Verdict: NOT ADOPTABLE — production v5 stays.**

## Method notes and caveats

- The halves variant is defined on the top-5 only: the halves training labels (sot_halves_combined.csv) cover 94.4% of the top-5 spine but no lower divisions, so both variants are gated on identical top-5 test matches; the full-pooled v5 figure above is the continuity check.
- Halves training coverage by era (top-5): 2020/21 onward ~100% except one F1 match; 2019/20 82% (F1 nearly absent); 2017/18–2018/19 partial (F1/SP1 holes). The per-half stores therefore learn early seasons from fewer matches; test-season coverage is 100% except one F1 match in 2023/24 (a test match needs no label — labels are training data; its FT total grades it).
- The halves member has no shots/BB component (the halves dataset carries SOT splits only, not shots splits), so read the halves delta against v5-nobb as well as against full v5: v5-nobb isolates what dropping BB costs, halves-vs-nobb isolates the halves engine.
- HT-state probabilities come from a goals regression on HTHG/HTAG with the same frozen lambda=100 (not separately tuned) and independent Poissons; the three multipliers are the only new fitted parameters and were frozen from pre-2023/24 walk-forward predictions.
- The state multipliers are pooled across divisions and both teams (by the team's own state); per-division multipliers were not attempted — the warm-up counts do not support five-way splits for the trailing state in smaller divisions.
- Script runtime: 71s. No production code touched; no odds anywhere (accuracy/calibration only).
