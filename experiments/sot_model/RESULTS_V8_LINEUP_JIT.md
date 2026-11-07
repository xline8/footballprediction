# Model SOT v8 — Susunan Pemain Asli (JIT) sebagai Penyesuai (eksperimen, BUKAN produksi)

## Ringkasan (Bahasa Indonesia)

Pertanyaan: model produksi v5 memprediksi di pagi hari, sebelum susunan pemain (starting XI) ada. Susunan resmi terbit ~1 jam sebelum kickoff. Kalau pada titik just-in-time itu perkiraan tembakan ke gawang (SOT) tiap tim disesuaikan dengan seberapa besar porsi produksi SOT terakhir tim itu yang duduk DI LUAR starting XI (pemain kunci absen), apakah prediksinya membaik?

Jawaban: **TIDAK — tidak ada varian yang lolos gerbang**. Pada 5.255 laga uji lima liga top (2023/24–2025/26), log loss garis 9,5 v5 = 0.6488; setiap varian penyesuaian dengan k > 0 justru MEMBURUK (terbaik sotA/shotA 0.6540, dan kalibrasinya runtuh ke ~5pp), sedangkan shotB memilih k = 0 — artinya datanya sendiri berkata "jangan disesuaikan". Kenapa: porsi produksi yang "hilang" rata-rata 0,56 per tim per laga — tapi itu kebanyakan massa pemain pinggiran dan pemain yang sudah pindah klub, bukan bintang yang absen (pemain dengan porsi SOT terbesar memang absen di 39,9% laga-tim, jadi sinyal bintangnya ada — hanya tenggelam di dalam ukuran agregatnya). Penyesuaiannya akhirnya bertindak seperti pemangkasan rata ke bawah yang tidak dibutuhkan model yang sudah terkalibrasi.

Implikasi produksi (apa pun hasilnya): penyesuaian ini HANYA bisa dipakai oleh langkah penyegaran prediksi menjelang kickoff (~1 jam sebelum laga, saat susunan pemain terbit). Model pagi tidak bisa memakainya. Produksi TIDAK diubah oleh eksperimen ini — keputusan adopsi ada di tangan user setelah membaca laporan ini.

## Reference reproduction check

Production v5 (slim+R+NB+BB) recomputed by run_sot_v5's own passes over ALL divisions: pooled line-9.5 log loss **0.6304** (RESULTS_V5.md: 0.6304) -> **MATCH**. Frozen v5 choices re-derived from warm-up only: ridge lambda = 100, BB prior = 200, NB r = 79.94. On the identical evaluation subset (top-5 test matches in the FotMob store, n = 5,255) the base recomputed inside this experiment matches pass_eval's per-division numbers to 0.0e+00 log loss — the base being adjusted is exactly production v5.

## The adjustment

Per team and match: trailing player shares (365d decay) of team SOT (variants sot*) or of team shots (variants shot*) over store matches strictly before the match; missing_share = share mass of players not in the actual starting XI (bench counts fully missing in *B, half in *A). Both v5 ensemble members' per-team expectations are scaled by (1 - k * missing_share); the NB/50-50 ensemble machinery is otherwise unchanged. k tuned on 2022/23 only (grid 0.0-1.0 step 0.1, ties -> smaller k).

### Tuning on 2022/23 (top-5 store matches, line 9.5)

| Variant | n | LL(k=0) | best k | LL(best k) | Δ |
|---|---|---|---|---|---|
| sotB | 1,826 | 0.6467 | 0.1 | 0.6466 | -0.0001 |
| sotA | 1,826 | 0.6467 | 0.1 | 0.6457 | -0.0010 |
| shotB | 1,826 | 0.6467 | 0 | 0.6467 | +0.0000 |
| shotA | 1,826 | 0.6467 | 0.1 | 0.6459 | -0.0008 |
| sotA+ret | 1,826 | 0.6467 | k=0.2, kb=0.3 | 0.6440 | -0.0026 |

## How much production is actually missing? (test seasons, per team-match)

- sotB: mean 0.558, median 0.563, p90 0.728, max 1.000; missing > 0.10 in 99.4% of team-matches, > 0.20 in 99.0%.
- sotA: mean 0.463, median 0.463, p90 0.645, max 0.974; missing > 0.10 in 99.2% of team-matches, > 0.20 in 97.5%.
- shotB: mean 0.559, median 0.562, p90 0.715, max 0.962; missing > 0.10 in 99.6% of team-matches, > 0.20 in 99.5%.
- shotA: mean 0.463, median 0.462, p90 0.632, max 0.944; missing > 0.10 in 99.6% of team-matches, > 0.20 in 98.3%.
- The single largest trailing-SOT player is absent from the XI in 4,185 of 10,482 team-matches (39.9%).
- Return share (SOT share of XI players who were not in the previous XI): mean 0.085, p90 0.197.

## Headline — identical subset, line 9.5

| Variant | LogLoss | Brier | Calib err (pp) | MAE | ΔLL vs v5 |
|---|---|---|---|---|---|
| v5 (unadjusted) | 0.6488 | 0.2285 | 0.01 | 2.41 | — |
| sotB (k=0.1) | 0.6567 | 0.2320 | 5.87 | 2.42 | +0.0079 |
| sotA (k=0.1) | 0.6541 | 0.2308 | 4.87 | 2.42 | +0.0053 |
| shotB (k=0) | 0.6488 | 0.2285 | 0.01 | 2.41 | +0.0000 |
| shotA (k=0.1) | 0.6540 | 0.2308 | 4.88 | 2.42 | +0.0052 |
| sotA+ret (k=0.2, kb=0.3) | 0.6617 | 0.2340 | 7.19 | 2.44 | +0.0129 |

## By season — line 9.5 log loss

| Season | n | v5 | sotB | sotA | shotB | shotA | sotA+ret |
|---|---|---|---|---|---|---|---|
| 2023/24 | 1,752 | 0.6545 | 0.6655 | 0.6622 | 0.6545 | 0.6620 | 0.6680 |
| 2024/25 | 1,751 | 0.6470 | 0.6526 | 0.6505 | 0.6470 | 0.6505 | 0.6580 |
| 2025/26 | 1,752 | 0.6449 | 0.6521 | 0.6495 | 0.6449 | 0.6495 | 0.6591 |

## By division — line 9.5 log loss

| Div | n | v5 | sotB | sotA | shotB | shotA | sotA+ret |
|---|---|---|---|---|---|---|---|
| E0 | 1,140 | 0.6648 | 0.6687 | 0.6665 | 0.6648 | 0.6666 | 0.6725 |
| D1 | 917 | 0.6780 | 0.6889 | 0.6860 | 0.6780 | 0.6858 | 0.6966 |
| I1 | 1,140 | 0.6098 | 0.6115 | 0.6098 | 0.6098 | 0.6097 | 0.6156 |
| SP1 | 1,140 | 0.6314 | 0.6416 | 0.6380 | 0.6314 | 0.6382 | 0.6418 |
| F1 | 918 | 0.6697 | 0.6845 | 0.6814 | 0.6697 | 0.6812 | 0.6955 |

## Gate verdict

- sotB: pooled LL does NOT improve (+0.0079); calibration 5.87pp vs base 0.01pp (WORSE — fail); worst division ΔLL +0.0148 (limit +0.003) -> **not adoptable**.
- sotA: pooled LL does NOT improve (+0.0053); calibration 4.87pp vs base 0.01pp (WORSE — fail); worst division ΔLL +0.0117 (limit +0.003) -> **not adoptable**.
- shotB: pooled LL does NOT improve (+0.0000); calibration 0.01pp vs base 0.01pp (ok); worst division ΔLL +0.0000 (limit +0.003) -> **not adoptable**.
- shotA: pooled LL does NOT improve (+0.0052); calibration 4.88pp vs base 0.01pp (WORSE — fail); worst division ΔLL +0.0114 (limit +0.003) -> **not adoptable**.
- sotA+ret: pooled LL does NOT improve (+0.0129); calibration 7.19pp vs base 0.01pp (WORSE — fail); worst division ΔLL +0.0257 (limit +0.003) -> **not adoptable**.
- **No variant is adoptable — production v5 stays unchanged, and a JIT lineup step is not worth building on this evidence.**

## Method notes and caveats

- Information discipline: shares use store matches strictly before the predicted match; the ONLY same-match information used is the official starting XI/bench — exactly what is public ~1h before kickoff, which is the decision point being evaluated. The match's own shotmap is never used for its own prediction (it updates the trailing state only afterwards).
- Departed players: a transferred/retired player's decayed share keeps counting as 'missing' until it decays away (365d half-life), so missing_share is an upper bound on truly-absent production — one reason the tuned k, not the raw share, carries the effect size.
- The store starts 2022/23, so tuning-season shares warm up from zero during Aug-Oct 2022; the tuning grid sees a weaker version of the signal than the test seasons have. Test-season shares benefit from the full trailing window.
- Player shares are team-specific (a mid-season transfer's history stays at his old club) and use the house SOT counting rule (on-target, not blocked, not own goal), the rule already validated against the spine's HST/AST.
- Why it failed (the distribution section is the evidence): missing_share averages 0.56 — but that mass is mostly long-tail production (fringe players, occasional shooters, departed players still decaying), not star absence. The single top producer IS absent in 39.9% of team-matches, so the star signal exists, but the aggregate share drowns it: at any k > 0 the factor (1 - k * missing) acts mainly as a near-uniform downward scaling of a base that is already calibrated (calibration error explodes 0.01pp -> ~5pp). Tuning on 2022/23 understated this: the store had just started, share mass was still warming up, so the same k looked harmless there. An obvious follow-up hypothesis for a FUTURE round (not run here — testing it now would be fitting to the test set): restrict/renormalise shares to the current matchday squad (starters + bench + unavailable) so departed/fringe mass drops out, and validate on a fresh split.
- No odds anywhere: predictive accuracy/calibration only, not betting value.
- Script runtime (this run): 71s.
