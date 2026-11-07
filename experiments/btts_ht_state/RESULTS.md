# Eksperimen G-1 — BTTS via Integrasi Keadaan Turun Minum (HT-State)

## Ringkasan (Bahasa Indonesia)

Pertanyaan: apakah mengintegrasikan probabilitas pra-laga atas keadaan turun minum — distribusi skor babak 1 dari lambda DC incumbent, lalu gol babak 2 yang disyaratkan pada keadaan HT (tim tertinggal menekan lebih keras) — memperbaiki probabilitas BTTS model gol?

Jawaban: **TIDAK LOLOS GERBANG (verdict: FAIL)**. Pada 5,255 laga uji top-5 (2023/24–2025/26, set identik untuk kedua varian), log loss BTTS: incumbent 0.6835 vs varian 0.6828 (perbaikan +0.0007, syarat ≥ +0,001). Kalibrasi BTTS: incumbent -2.02pp vs varian -0.17pp. Cek must-not-worsen: OU 2.5 Δ -0.0002, 1X2 Δ -0.0005. Divisi paling memburuk: F1 (+0.0013, batas +0,003). Penyusutan pengali terpilih di tuning (2021/22–2022/23): s* = 1.0.

Produksi TIDAK diubah oleh eksperimen ini apa pun hasilnya. Sesuai desain item, PASS pun hanya ditandai untuk keputusan user (ini bedah paling berisiko di antara enam item), bukan adopsi otomatis.

Konteks pendahulu: mekanisme mengejar yang sama di SOT V6 (babak) GAGAL gerbangnya (0,6502 vs 0,6488). Hasil di sini harus dibaca dengan diskon yang sama.

## Gate (pre-registered)

- BTTS LL pooled membaik ≥0,001: **TIDAK** (+0.0007)
- Tidak ada divisi memburuk >0,003: **YA** (terburuk F1 +0.0013)
- Kalibrasi BTTS tidak memburuk (\|Δpp\|): **YA** (-2.02pp → -0.17pp)
- OU 2.5 & 1X2 tidak memburuk: **YA** (OU -0.0002; 1X2 -0.0005)
- **Verdict: FAIL**

## Headline — pooled test (top-5, 2023/24–2025/26)

| Pasar | LL inc | LL var | Δ (var-inc) | Pred inc | Pred var | Aktual | Kalib inc (pp) | Kalib var (pp) |
|---|---|---|---|---|---|---|---|---|
| BTTS | 0.6835 | 0.6828 | -0.0007 | 0.5292 | 0.5477 | 0.5494 | -2.02 | -0.17 |
| OU 2.5 | 0.6744 | 0.6742 | -0.0002 | 0.5260 | 0.5354 | 0.5378 | -1.18 | -0.24 |
| 1X2 | 0.9827 | 0.9822 | -0.0005 | — | — | — | — | — |

Reproduksi audit: incumbent pada pass ini membaca LL BTTS 0.6835 / OU 0.6744 — persis angka audit §1A (0,6835 / 0,6744). LL 1X2 0.9827 vs audit 0,9829: selisih hanya karena set gerbang di sini n=5.255 (satu laga tanpa HT di spine dikeluarkan dari KEDUA varian; audit n=5.256).

### Per divisi

| Div | n | BTTS LL inc | BTTS LL var | Δ | OU LL inc | OU LL var | Δ | 1X2 LL inc | 1X2 LL var | Δ |
|---|---|---|---|---|---|---|---|---|---|---|
| D1 | 917 | 0.6646 | 0.6634 | -0.0011 | 0.6511 | 0.6499 | -0.0012 | 0.9894 | 0.9892 | -0.0003 |
| E0 | 1,140 | 0.6804 | 0.6787 | -0.0017 | 0.6781 | 0.6770 | -0.0010 | 0.9772 | 0.9766 | -0.0007 |
| F1 | 918 | 0.6915 | 0.6927 | +0.0013 | 0.6827 | 0.6828 | +0.0001 | 1.0002 | 1.0007 | +0.0005 |
| I1 | 1,140 | 0.6934 | 0.6942 | +0.0008 | 0.6890 | 0.6895 | +0.0005 | 0.9823 | 0.9813 | -0.0010 |
| SP1 | 1,140 | 0.6854 | 0.6829 | -0.0025 | 0.6684 | 0.6687 | +0.0003 | 0.9692 | 0.9684 | -0.0007 |

### Per musim

| Musim | n | BTTS LL inc | BTTS LL var | Δ | OU LL inc | OU LL var | Δ | 1X2 LL inc | 1X2 LL var | Δ |
|---|---|---|---|---|---|---|---|---|---|---|
| 2023/24 | 1,752 | 0.6784 | 0.6766 | -0.0017 | 0.6666 | 0.6657 | -0.0009 | 0.9755 | 0.9747 | -0.0008 |
| 2024/25 | 1,751 | 0.6860 | 0.6853 | -0.0006 | 0.6734 | 0.6736 | +0.0002 | 0.9807 | 0.9806 | -0.0001 |
| 2025/26 | 1,752 | 0.6861 | 0.6863 | +0.0002 | 0.6833 | 0.6834 | +0.0001 | 0.9919 | 0.9914 | -0.0005 |

## Irisan keadaan HT aktual — apakah celah -8,5pp menyusut?

| HT state (aktual) | n | Pred inc | Pred var | Aktual | Celah inc (pp) | Celah var (pp) |
|---|---|---|---|---|---|---|
| away_leading | 1,372 | 0.5378 | 0.5563 | 0.6224 | -8.47 | -6.61 |
| home_leading | 1,781 | 0.5303 | 0.5488 | 0.5677 | -3.74 | -1.89 |
| level | 2,102 | 0.5227 | 0.5410 | 0.4862 | +3.65 | +5.48 |

Catatan irisan: keadaan HT adalah informasi pasca-laga; irisan ini diagnostik lokalisasi error (seperti di audit), bukan fitur. Varian tidak pernah melihat HT aktual — ia mengintegrasikan atas distribusi HT pra-laga, jadi penyusutan celah di sini adalah bukti mekanisme bekerja, bukan kebocoran.

## Pembacaan jujur (dekomposisi efek)

- Kenaikan prediksi BTTS varian per irisan HT aktual hampir SERAGAM: away-leading +1.86pp, home-leading +1.85pp, level +1.83pp. Komponen diskriminasi-keadaannya (sebaran antar-irisan) hanya ~0,02pp — hampir seluruh efek adalah kenaikan global (± seragam) probabilitas BTTS, bukan pemilahan per keadaan. Itu sebabnya celah irisan tertinggal menyusut (karena di sana incumbent paling rendah) tetapi celah irisan level justru membesar (+3.65pp → +5.48pp).
- Sumber kenaikan global: pengali tidak simetris (trail ≈ ×1,11 vs lead ≈ ×0,99), jadi mengintegrasikan atas keadaan HT menaikkan total gol babak-2 yang diharapkan, bukan sekadar mengalokasikannya ulang. Pra-laga, distribusi keadaan HT mirip antar-laga, sehingga yang bisa dieksploitasi memang sebagian besar komponen seragam ini — dekat dengan rekalibrasi global, keluarga yang sudah pernah diuji dan dikembalikan di EXPERIMENTS_LOG E3.
- Efek meluruh antar-musim uji: ΔLL BTTS -0.0017 (2023/24) → -0.0006 (2024/25) → +0.0002 (2025/26, memburuk). Keuntungan terkonsentrasi di musim uji pertama dan hilang sesudahnya — pola under-prediksi BTTS era tuning yang tidak persisten, bukan sinyal keadaan yang stabil.
- Kesimpulan: mekanisme mengejar itu NYATA (pengali trail ×1,11 stabil di semua cutoff walk-forward; celah −8,5pp menyusut ke −6,6pp), tetapi porsi yang bisa diprediksi pra-laga terlalu kecil dan terlalu seragam untuk melewati gerbang 0,001 — persis pola kegagalan pendahulunya, SOT V6. FAIL diterima apa adanya; tidak ada penyelamatan lewat tuning ulang pada data uji.

## Parameter (walk-forward per musim uji)

| Musim uji | Cutoff estimasi | n estimasi | Alpha (porsi gol B1) | ×lead | ×trail | ×level |
|---|---|---|---|---|---|---|
| 2023/24 | 2023-08-11 | 10,526 | 0.4431 | 0.989 | 1.111 | 1.001 |
| 2024/25 | 2024-08-15 | 12,278 | 0.4429 | 0.992 | 1.117 | 0.998 |
| 2025/26 | 2025-08-15 | 14,029 | 0.4438 | 0.981 | 1.117 | 0.997 |

## Tuning s (hanya 2021/22–2022/23; parameter juga walk-forward per musim)

| s | BTTS LL varian (tuning) | BTTS LL incumbent (tuning) |
|---|---|---|
| 0.0 | 0.6880 | 0.6880 |
| 0.25 | 0.6877 | 0.6880 |
| 0.5 | 0.6874 | 0.6880 |
| 0.75 | 0.6872 | 0.6880 |
| 1.0 | 0.6872 | 0.6880 | ← s*

## Method notes

- Incumbent direkomputasi dalam pass yang sama dari records_cache (p_btts/p_over_dc/ph_dc tersimpan = output DC.probs dari lambda dan rho yang sama) pada set laga yang persis sama dengan varian.
- Varian = incumbent yang digeser oleh selisih integrasi: logit(p_var) = logit(p_inc) + logit(p_int(m_s)) − logit(p_int(m=1)) untuk BTTS/OU; analog log ternormalisasi untuk 1X2. Pada s=0 varian identik dengan incumbent, dan koreksi tau DC tidak dihitung ganda karena integrasi murni-Poisson hanya menyumbang selisihnya.
- Integrasi: babak 1 Poisson(alpha·λ), babak 2 Poisson((1−alpha)·λ·pengali keadaan HT), keadaan = unggul/level/tertinggal dari skor HT; BTTS dan OU dihitung tertutup dari massa HT yang relevan, 1X2 dari massa HT per (keadaan, selisih) × distribusi selisih babak 2.
- Pengali diestimasi sebagai Σ gol babak-2 aktual / Σ lambda babak-2 dasar pada record walk-forward sebelum musim berjalan (bukan rasio mentah — lambda mengendalikan confounding kekuatan tim: tim unggul cenderung memang lebih kuat).
- Tidak ada odds; akurasi/kalibrasi saja. Tidak ada file produksi yang diubah; tidak ada tuning apa pun pada data uji.
- Runtime skrip: ~37.9 dtk.
