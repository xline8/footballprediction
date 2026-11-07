# Corner Territorial-Dominance Multiplier (C-1) — Hasil Eksperimen

## Ringkasan (Bahasa Indonesia)

Eksperimen ini menguji usulan audit 2026-11-07 §2C item C-1: menambahkan
pengali `exp(β·z)` pada mean model corner produksi (shot-based CS,
`mu_cs`), dengan `z` = selisih dominasi teritorial trailing-10 laga dari
gudang FotMob (`shot_lineup_features.csv`) — selisih penguasaan bola dan
selisih big chances, kandang minus tandang, dihitung ketat hanya dari laga
sebelum laga yang diprediksi. Beta di-fit hanya di musim 2022/23 + 2023/24
(n fit = 3,267); pengujian di 2024/25 + 2025/26 pada set identik
(n test = 3,433) dengan incumbent (β=0) dihitung ulang dalam pass
yang sama memakai gamma*/r* produksi yang sama.

Hasil kunci (set test identik): log loss garis 9.5 incumbent
**0.6855** vs varian **0.6841**
(perbaikan +0.0013); ΔLL per musim:
2024/25 -0.0009, 2025/26 -0.0018;
kalibrasi @9.5 (pred − aktual) -0.78pp → -0.76pp.
Beta ter-fit: β_possession = +0.00095 per poin persen,
β_bigchance = -0.00515 per big chance/laga.

Gerbang **LULUS (PASS)**: pengali teritorial memperbaiki log loss pooled garis 9.5 melewati ambang 0.001, tidak ada musim test yang memburuk, dan kalibrasi tidak membesar. Kandidat layak adopsi — tetapi produksi TIDAK diubah oleh eksperimen ini; adopsi menunggu keputusan bos (lihat bagian Catatan adopsi).

Kemiringan residual di bucket ekstrem pada set test ini — possession:
bucket terbawah -0.210 → -0.068,
bucket teratas +0.163 → +0.018;
big chances: terbawah +0.006 → +0.020,
teratas +0.338 → +0.315
(angka audit asli +0.20/+0.32 diukur di jendela 2023/24–2025/26 dengan
artefak tersimpan; di sini perbandingan yang sah adalah incumbent-vs-varian
pada set test yang sama).

## Desain (pra-registrasi)

- Varian: `mu_var = mu_cs * clamp(exp(β_p·z_poss + β_b·z_bc), 0.70, 1.43)`;
  distribusi NB dan r* produksi (1.1868) tidak berubah; gamma*
  produksi = 0.15.
- z: trailing-10 (min 5 laga) per tim dari `shot_lineup_features.csv`,
  konstruksi persis `trailing()` di `experiments/audit_models_2026_11_07.py`;
  z_match = trailing_diff(tim kandang) − trailing_diff(tim tandang).
  Tidak ada kebocoran laga yang sama (strictly `date < tanggal laga`).
- Fit β: minimisasi mean NLL NB total corner di jendela fit saja
  (r* tetap); optimum diverifikasi dengan `nll_row` eksak produksi:
  NLL fit 2.6039 (β=0) →
  2.6029 (β ter-fit).
- Laga tanpa z lengkap dibuang dari KEDUA model (set identik):
  mentah per musim {'2022/23': 1826, '2023/24': 1752, '2024/25': 1751, '2025/26': 1752}, dibuang {'2022/23': 246, '2023/24': 65, '2024/25': 40, '2025/26': 30}
  (penyebab utama: tim promosi/awal 2022/23 belum punya ≥5 laga warehouse).
- Clamp pengali mengikat pada 0.00% laga test
  (rentang mentah exp(β·z) di test: 0.951–1.064).

## Hasil test — pooled

**Pooled test 2024/25 + 2025/26** (n=3433)

| Garis | LL incumbent | LL varian | ΔLL (var−inc) | Kalibrasi inc (pp) | Kalibrasi var (pp) |
|---|---|---|---|---|---|
| 8.5 | 0.6661 | 0.6653 | -0.0008 | +0.26 | +0.26 |
| 9.5 | 0.6855 | 0.6841 | -0.0013 | -0.78 | -0.76 |
| 10.5 | 0.6563 | 0.6552 | -0.0011 | -0.56 | -0.53 |

Aktual Over rate @9.5 pada set test: 49.29%.

## Hasil test — per musim (garis 9.5)

| Musim | n | LL incumbent | LL varian | ΔLL (var−inc) | Kalibrasi inc (pp) | Kalibrasi var (pp) |
|---|---|---|---|---|---|---|
| 2024/25 | 1711 | 0.6841 | 0.6832 | -0.0009 | -0.80 | -0.79 |
| 2025/26 | 1722 | 0.6868 | 0.6850 | -0.0018 | -0.76 | -0.73 |

## Kemiringan residual per bucket dominasi (set test, residual = aktual − mu)

Bucket possession (edges −8/−3/+3/+8, sama seperti audit):

| Bucket | n | Rata-rata z_poss | Resid incumbent | Resid varian |
|---|---|---|---|---|
| 0: z < −8 | 1168 | -21.5 | -0.210 | -0.068 |
| 1: −8 ≤ z < −3 | 340 | -5.5 | -0.214 | -0.178 |
| 2: −3 ≤ z < +3 | 403 | +0.0 | +0.064 | +0.060 |
| 3: +3 ≤ z < +8 | 362 | +5.4 | +0.145 | +0.099 |
| 4: z ≥ +8 | 1160 | +21.2 | +0.163 | +0.018 |

Bucket big chances (edges −1.5/−0.5/+0.5/+1.5):

| Bucket | n | Rata-rata z_bc | Resid incumbent | Resid varian |
|---|---|---|---|---|
| 0: z < −1.5 | 628 | -2.52 | +0.006 | +0.020 |
| 1: −1.5 ≤ z < −0.5 | 696 | -1.04 | -0.285 | -0.277 |
| 2: −0.5 ≤ z < +0.5 | 810 | -0.04 | -0.119 | -0.115 |
| 3: +0.5 ≤ z < +1.5 | 643 | +0.93 | +0.029 | +0.013 |
| 4: z ≥ +1.5 | 656 | +2.41 | +0.338 | +0.315 |

## Eksploratori (BUKAN gerbang; di-fit di jendela fit yang sama)

| Varian satu-fitur | β ter-fit | LL@9.5 test | ΔLL vs incumbent |
|---|---|---|---|
| possession saja | +0.00072 | 0.6839 | -0.0015 |
| big chances saja | +0.00125 | 0.6853 | -0.0002 |

## Pemeriksaan kewarasan

- Incumbent yang dihitung ulang vs artefak tersimpan
  `predictions_corners_shots.csv` pada laga test yang tumpang tindih:
  dibandingkan 3433 laga, selisih maks
  |mu| = 0.0050,
  selisih maks |p@9.5| = 0.0000
  (konsisten dengan pembulatan artefak: mu 2 desimal, p 4 desimal).
- Beta di-fit hanya dari jendela fit; tidak ada parameter yang menyentuh
  musim test. Gamma*/r* adalah parameter produksi yang di-fit di jendela
  validasi lama (2019/20–2020/21), jauh sebelum kedua jendela di sini.

## Diagnostik kekokohan & interpretasi (bukan gerbang)

- Optimizer: 7 start Nelder-Mead konvergen ke β yang sama
  (β_poss +0.00095, β_bc -0.00515; rincian per start
  di metrics.json) — optimum bukan artefak titik awal.
- Kolinearitas: corr(z_poss, z_bc) = 0.54 di
  jendela fit (sd z_poss 20.0 poin,
  sd z_bc 1.68/laga). Efek per 1 sd:
  possession +0.0190 log-mu,
  big chances -0.0087 log-mu.
  Tanda β_bc yang negatif adalah koefisien parsial di hadapan possession
  (fit big-chances-saja ≈ +0.00125, praktis nol): sinyal
  teritorialnya dibawa possession; big chances tidak menambah apa-apa di
  luar possession + tembakan yang sudah dipakai model. Ini konsisten
  dengan peringatan audit bahwa possession/big chances berkorelasi dengan
  tembakan.
- Ketidakpastian paired (diagnostik): ΔLL@9.5 per laga di test rata-rata
  -0.00135 dengan SE
  0.00060 (t ≈ -2.23);
  53.1% laga membaik.
  Gain pooled +0.0013 hanya sedikit di atas ambang 0.001 —
  lolos gerbang pra-registrasi, tetapi marginnya tipis dan efeknya memang
  kelas kecil seperti perkiraan audit (~0.001).
- Di jendela fit sendiri, LL@9.5 biner: incumbent
  0.6881 → varian
  0.6870 (fit memang membaik juga,
  bukan hanya test).
- Kemiringan possession di bucket ekstrem menyusut besar (bucket teratas
  +0.163 → +0.018;
  terbawah -0.210 → -0.068)
  karena rata-rata |z_poss| di bucket ekstrem ≈ 21 poin sehingga pengali
  ≈ exp(±0.02) ≈ ±2% pada mu ≈ ±0.2 corner. Kemiringan big chances di
  bucket teratas nyaris tidak bergerak
  (+0.338 → +0.315) —
  sesuai koefisien parsialnya yang ≈ nol/negatif kecil.

## Putusan gerbang

| Syarat | Ambang | Hasil | Status |
|---|---|---|---|
| 1. Gain LL@9.5 pooled | ≥ 0.001 | +0.0013 | LULUS |
| 2. Tak ada musim test memburuk | ΔLL ≤ 0 di kedua musim | 2024/25 -0.0009, 2025/26 -0.0018 | LULUS |
| 3. Kalibrasi tidak membesar | \|var\| ≤ \|inc\| | -0.78pp → -0.76pp | LULUS |

**VERDICT: PASS**

## Catatan adopsi (hanya relevan bila PASS dan bos menyetujui)

Perubahan yang dibutuhkan di `model_corners_v3.py` bila varian ini diadopsi:

1. `predict_upcoming()`: mu saat ini dihitung dari
   `mu_cs({base_h, base_a, fhp, fhc, fap, fac}, gamma)`. Adopsi menambah
   satu langkah sesudahnya: `mu *= territorial_multiplier(home, away, date)`
   dengan β dibaca dari `ta/corner_params.json` (skema JSON diperluas:
   `beta_poss`, `beta_bc`; penulisan parameter di `_run_backtest()` harus
   ikut menulisnya — tetapi β TIDAK bisa di-fit di `_run_backtest` biasa
   karena jendela fit-nya butuh fitur warehouse; fit β perlu langkah
   tersendiri dari skrip eksperimen ini, dijalankan saat refit).
2. Input baru saat prediksi: `shot_lineup_features.csv` harus dimuat di
   `predict_upcoming()` untuk membangun agregat trailing-10 possession &
   big-chances per tim (fungsi `build_trailing_index`/`trailing` di skrip
   ini bisa dipindah apa adanya), dinormalisasi namanya dengan
   `football_etl.normalize_name` karena nama FotMob ≠ nama football-data.
3. Ketersediaan untuk fixture mendatang: YA untuk pasangan tim top-5 yang
   keduanya sudah punya ≥5 laga warehouse sebelum tanggal fixture (gudang
   mencakup semua laga liga top-5 sejak 2022/23 dan terus diperbarui oleh
   pull FotMob). TIDAK selalu untuk tim promosi di awal musim (belum 5 laga
   di divisi teratas) — untuk kasus itu fallback yang aman adalah pengali
   1.0 (perilaku incumbent). Catatan: fitur warehouse adalah data laga yang
   SUDAH dimainkan, jadi trailing untuk fixture masa depan selalu bisa
   dihitung dari file yang ada pada saat prediksi, tanpa pull baru.

## Reproduksi

```
.venv/bin/python experiments/corner_territorial/run_experiment.py
```

Menghasilkan ulang: `predictions_test.csv`, `metrics.json`, `RESULTS.md`
di direktori ini. Tidak ada file produksi yang ditulis.
