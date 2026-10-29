# EXPERIMENT_EDGE_BAND — re-validasi live-pick edge band

Eksperimen-and-verdict. **Produksi tidak diubah** (`make_picks_live.py` tetap
memakai `EDGE_LO/EDGE_HI = 0.20/0.22`, `ODDS_LO/ODDS_HI = 1.20/1.50`).

Menjawab: apakah band edge produksi memiliki edge nyata?

- **edge** = `p_meta(home) - p_fair_shin(home)` (opening odds B365)
- home-win only, flat 1u, settle di `odds_open`
- meta 9-logit walk-forward bulanan (leak-free), records `blend`
- diagnostics 2017/18–2022/23 → grid; confirmation 2023/24–2025/26 → 2 rule

## Hasil

| metrik | nilai |
|---|---|
| kandidat home-win TOP5 | 15.494 |
| distribusi edge (semua musim) | mean −0.0023, std 0.0123, max +0.0832 |
| fraction edge ≥ 0.05 | 0.0014 (0,14%) |
| fraction edge ≥ 0.10 | 0,0000 |
| fraction edge ≥ 0.20 | 0,0000 |

Landscape diagnostics (yield per-pick): setiap threshold ≥ 0.05 punya **< 100
pick**; threshold ≥ 0.10 **0 pick**. Jadi tidak ada "best simple threshold" yang
memenuhi kriteria (≥ 100 pick diagnostic) → T* tidak dievaluasi.

## R1 (band produksi)

- Frekuensi historis: **0 pick** di seluruh 68.763 records (semua musim).
- Confirmation: n=0; yield n/a.

## Verdict

**UNVALIDATED.** Band produksi `edge ∈ [0.20, 0.22)` hampir tidak pernah
terjadi (max edge keseluruhan hanya +0.083). Jalur live bersifat dekoratif:
filter tidak pernah memicu pick, sehingga tidak ada edge yang dieksploitasi —
dan tidak ada yang perlu diganti (REPLACE tidak relevan, T* pun tidak ada).

Ini mengonfirmasi peringatan yang sudah tertulis di `make_picks_live.py`
(2026-10-26): dengan de-vigging Shin yang benar, edge ≥ 0.20 pada favorit
1.2–1.5 tidak pernah muncul. Hasil ini konsisten dengan temuan efisiensi pasar
1X2 (tidak ada rule uji menghasilkan ROI positif signifikan).
