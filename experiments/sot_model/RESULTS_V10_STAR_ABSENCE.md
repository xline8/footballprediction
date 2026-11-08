# Model SOT v10 — Uji Absennya Penembak Dominan ("bintang absen") (eksperimen, BUKAN produksi)

## Ringkasan (Bahasa Indonesia)

Pertanyaan (klaim user): kalau pemain bintang — penembak yang sungguh dominan — absen, apakah SOT timnya benar-benar berkurang? V10 mengujinya dalam bentuk paling murni: hanya laga-tim di mana pemain dengan porsi trailing SOT terbesar ≥25% (porsi dihitung bebas bocor dari laga-laga sebelumnya saja) benar-benar tidak tampil semenit pun — bukan sekadar tidak jadi starter seperti di V8. Ekspektasinya adalah ekspektasi produksi v5 di luar sampel (kedua jangkar reproduksi cocok persis: pooled 0,6304, subset 0,6488), pada 7.081 laga lima liga top 2022/23–2025/26.

Jawaban: **TIDAK TERBUKTI — datanya justru menunjuk ke arah sebaliknya.** Pada ambang utama 25% ada **217 laga-tim dominan-absen** (nama-namanya memang bintang sungguhan: Mbappé 20×, Haaland 19×, Balogun 14×, Mitrović 10×, Kane 8×, dst.; 176 di antaranya bahkan tidak ada di daftar skuad hari laga). Di laga-laga itu tim mencetak rata-rata **+0,227 SOT DI ATAS** ekspektasi v5 (agregat **+5,0%**), dengan interval kepercayaan 95% [−0,067, +0,521] — mencakup nol dan sebagian besar positif. Kontrolnya (penembak dominan tampil, n = 1.371) nyaris pas: −0,038. Pola dosis antar ambang juga tidak mendukung klaim: residual absen +0,011 di ambang 20% (n = 798, persis sama dengan kontrolnya), +0,227 di 25%, dan −0,174 di 30% — tetapi di 30% n tinggal 45 dan intervalnya sangat lebar [−0,717, +0,368], jadi angka itu tidak membuktikan apa-apa; urutan antar ambang tidak monoton. Per musim pun tandanya berbalik-balik (2022/23 −0,404; 2023/24 +0,464; 2024/25 +1,528 pada n = 32; 2025/26 −0,099 pada n = 10) — tidak ada efek yang stabil.

Kenapa bisa begitu (interpretasi yang konsisten dengan kegagalan V8): tembakan tim tidak hilang bersama bintangnya — tembakannya berpindah ke pemain lain, dan ekspektasi v5 yang berbasis tim sudah menghargai produksi rata-rata tim, bukan produksi satu pemain. Jadi penyesuaian "bintang absen" tidak punya bahan bakar: pengukuran sekunder (satu faktor penyesuaian) **tidak dijalankan** karena syarat praregistrasinya (efek primer nyata) tidak terpenuhi, dan **tidak ada rekomendasi bangun**. Produksi tidak diubah. Intuisi user mendapat putusan jujur dari data: pada level tim, absennya penembak dominan tidak menggerakkan total SOT secara terukur.

## Praregistrasi

Desain eksperimen ini ditulis ke file ini sebelum skrip hasil dijalankan. Tidak ada statistik hasil (residual, tingkat absen per ambang, log loss subset) yang dihitung sebelum bagian Desain ini selesai ditulis. Yang sudah diperiksa sebelum praregistrasi hanyalah STRUKTUR data (field JSON gudang FotMob: daftar starter, daftar pemain pengganti beserta `substitutionEvents`, daftar `unavailable`, shotmap) dan jumlah baris indeks gudang — bukan statistik hasil.

Latar: user berpendapat bahwa bila pemain bintang absen, tembakan ke gawang (SOT) tim pasti berkurang. Eksperimen V8 (RESULTS_V8_LINEUP_JIT.md) menguji penyesuaian berdasarkan porsi produksi yang hilang secara AGREGAT (rata-rata 0,56 per laga-tim, didominasi pemain pinggiran dan pemain yang sudah pindah) dan gagal total di gerbang. V10 menguji klaim user dalam bentuknya yang paling murni: hanya laga di mana penembak yang SUNGGUH DOMINAN absen — irisan yang di V8 tenggelam di dalam agregat.

## Desain (dikunci sebelum run)

### Kerangka data

- Laga liga lima besar (E0, D1, I1, SP1, F1) yang ada di gudang FotMob (`data_enrichment/fotmob_full/`) dengan lineup dan shotmap, musim **2022/23–2025/26** (kerangka yang sama dengan validasi v5/V8; 2026/27 tidak dipakai). Perkiraan ±7.081 laga = ±14.162 laga-tim sebelum filter riwayat minimum.
- Aktual SOT per tim: kolom HST/AST file bersih (label terverifikasi). Sebagai pemeriksaan silang, total shotmap per tim (aturan rumah) dibandingkan dengan HST/AST dan tingkat kesepakatannya dilaporkan.

### Porsi penembak trailing (bebas bocor)

- Untuk setiap laga-tim, porsi tiap pemain = SOT pemain / SOT tim, dihitung HANYA dari laga-laga gudang tim itu yang STRICTLY SEBELUM laga ini (jendela expanding, TANPA decay — perbedaan yang disengaja dari V8, dinyatakan di sini; jendela expanding membuat definisi "penembak utama yang sudah mapan" stabil dan bebas parameter tambahan).
- Porsi bersifat spesifik-tim: produksi pemain di klub lama tetap tercatat di klub lama (aturan sama seperti V8).
- Aturan hitung SOT rumah: tembakan `isOnTarget`, bukan `isBlocked`, bukan `isOwnGoal` — aturan yang sama yang tervalidasi terhadap HST/AST.
- Kelayakan: laga-tim hanya masuk semesta analisis bila timnya sudah punya **≥5 laga gudang sebelumnya** (porsi dari riwayat lebih pendek dianggap belum terdefinisi).

### Definisi dominan & absen

- **Penembak dominan** suatu laga-tim = pemain dengan porsi trailing TERBESAR di tim itu, bila porsi terbesar itu ≥ ambang. Ambang utama **25%**; sensitivitas **20%** dan **30%**.
- **Tampil (appeared)** = pemain ada di starting XI, ATAU pemain pengganti yang benar-benar masuk (ada event `subIn` di `performance.substitutionEvents` pada data lineup), ATAU tercatat melepaskan tembakan di shotmap laga itu (pemeriksaan kewarasan: penembak pasti berada di lapangan).
- **Absen** = penembak dominan TIDAK tampil sama sekali menurut definisi di atas (mencakup: tidak ada di daftar skuad hari laga, ada di daftar `unavailable`, atau duduk di bangku cadangan tanpa masuk).
- Klasifikasi primer per laga-tim: **dominan-absen** vs **dominan-tampil** (kontrol). Sebagai deskripsi tambahan dilaporkan juga rincian keadaan pemain dominan yang absen (di daftar unavailable / bangku cadangan tak terpakai / tidak ada di daftar mana pun) dan nama-nama yang paling sering muncul sebagai dominan-absen.

### Ekspektasi model (di luar sampel, jujur)

- Ekspektasi SOT per tim = ekspektasi produksi v5 walk-forward: 0,5 × anggota regresi+BB + 0,5 × anggota naif, dihitung dengan mesin yang sama persis dengan V8 (yang terverifikasi mereproduksi pass_eval v5). Dua jangkar wajib cocok, kalau tidak run dinyatakan tidak sah: (1) log loss pooled garis 9,5 seluruh divisi = **0,6304** (RESULTS_V5.md); (2) log loss basis pada subset uji top-5 2023/24–2025/26 = **0,6488** (RESULTS_V8_LINEUP_JIT.md).
- Jadwal panggilan mesin meniru V8: pass terpisah untuk 2022/23 (jadwal pass_tune) dan untuk musim uji 2023/24–2025/26 (jadwal pass_eval), karena RegressionStore melakukan refit malas yang jadwalnya bergantung pada urutan panggilan per divisi.

### Pengukuran primer (klaim user, diuji langsung)

Untuk setiap ambang (20/25/30%), pada laga-tim dominan-absen dan dominan-tampil (kontrol):

- n, rata-rata ekspektasi, rata-rata aktual;
- **rata-rata residual** (aktual − ekspektasi) beserta **interval kepercayaan 95%** (aproksimasi normal: mean ± 1,96 × sd/√n);
- **kekurangan agregat %** = (Σaktual − Σekspektasi) / Σekspektasi × 100%;
- rata-rata kekurangan per kasus % (rata-rata dari residual/ekspektasi per laga-tim).

Pola dosis: kekurangan harus membesar (makin negatif) saat ambang naik 20% → 25% → 30% bila efeknya nyata (kasus makin murni bintangnya).

**Aturan putusan efek nyata (dikunci):** efek dinyatakan NYATA hanya bila pada ambang utama 25%: rata-rata residual dominan-absen < 0 DAN seluruh interval kepercayaan 95%-nya di bawah 0. Di luar itu, efek dinyatakan tidak terbukti pada data ini — apa pun yang ditunjukkan ambang lain (ambang lain hanya sensitivitas).

### Pengukuran sekunder (hanya bila efek primer nyata)

- Satu parameter penyesuaian: faktor multiplikatif `f` pada ekspektasi tim yang penembak dominannya absen (diterapkan ke kedua anggota ensemble, seperti faktor V8), dicari pada grid 0,80–1,00 langkah 0,01 dengan meminimalkan log loss garis 9,5 pada SUBSET laga tuning (laga dengan minimal satu tim dominan-absen pada ambang 25%).
- Musim tuning: **2022/23 + 2023/24**. Musim validasi: **2024/25 + 2025/26**.
- **Mini-gate (dikunci sebelum angka validasi):** penyesuaian dinyatakan lolos hanya bila di validasi: (1) log loss subset membaik vs tanpa penyesuaian (f = 1), DAN (2) log loss pooled semua laga validasi tidak memburuk lebih dari **0,0005**.
- Bila mini-gate lolos: hasilnya adalah REKOMENDASI bangun (langkah JIT terpisah), BUKAN perubahan produksi — eksperimen ini tidak menyentuh produksi dalam keadaan apa pun.
- Sebagai referensi deskriptif dilaporkan juga faktor pencocok-rata-rata pada tuning (Σaktual/Σekspektasi laga-tim dominan-absen).

### Yang tidak dilakukan eksperimen ini

- Tidak ada perubahan file produksi, cron, atau `run_daily_shadow.py`.
- Tidak ada ambang, definisi, atau parameter lain yang dicari-cari di luar yang tertulis di atas.
- Tidak ada odds: akurasi prediksi saja, bukan nilai taruhan.

## Hasil

Validitas run: jangkar pooled v5 = 0.6304 (target 0.6304) -> COCOK; log loss basis subset uji = 0.6488 (target 0.6488, n = 5,255) -> COCOK. Kedua jangkar cocok — angka di bawah sah.

Kerangka terkumpul: 1,826 laga 2022/23 + 5,255 laga 2023/24–2025/26 = 7,081 laga. Pemeriksaan silang aktual: total SOT shotmap per tim sama persis dengan HST/AST pada 13,536 dari 14,162 laga-tim (95.6%).

### Pengukuran primer — residual (aktual − ekspektasi v5) per laga-tim

| Ambang | Kelompok | n | Rata-rata eksp. | Rata-rata aktual | Rata-rata residual [IK 95%] | Kekurangan agregat | Rata-rata per kasus |
|---|---|---|---|---|---|---|---|
| 20% | dominan ABSEN | 798 | 4.48 | 4.49 | +0.011 [-0.148, +0.170] | +0.2% | -1.7% |
| 20% | dominan tampil (kontrol) | 3,307 | 4.47 | 4.48 | +0.011 [-0.066, +0.088] | +0.2% | -0.7% |
| 25% | dominan ABSEN | 217 | 4.54 | 4.77 | +0.227 [-0.067, +0.521] | +5.0% | +3.3% |
| 25% | dominan tampil (kontrol) | 1,371 | 4.52 | 4.48 | -0.038 [-0.156, +0.080] | -0.8% | -1.5% |
| 30% | dominan ABSEN | 45 | 4.31 | 4.13 | -0.174 [-0.717, +0.368] | -4.0% | -6.2% |
| 30% | dominan tampil (kontrol) | 383 | 4.55 | 4.51 | -0.033 [-0.257, +0.191] | -0.7% | -1.6% |

Putusan efek (aturan terkunci, ambang 25%): rata-rata residual dominan-absen = +0.227 dengan IK 95% [-0.067, +0.521] -> efek **TIDAK TERBUKTI**. Kontrol dominan-tampil pada ambang yang sama: -0.038 [-0.156, +0.080] (n = 1,371). Pola dosis antar ambang terlihat pada tabel: kekurangan agregat absen 20%: +0.2%, 25%: +5.0%, 30%: -4.0%.

### Karakterisasi kasus dominan-absen (ambang 25%, deskriptif)

- tidak ada di daftar skuad hari laga: 176 laga-tim
- terdaftar unavailable (cedera/skorsing): 21 laga-tim
- di bangku cadangan, tidak dimainkan: 20 laga-tim
- Paling sering absen sebagai penembak dominan: Kylian Mbappé (20×); Erling Haaland (19×); Folarin Balogun (14×); Aleksandar Mitrovic (10×); Vedat Muriqi (9×); Enes Ünal (9×); Marvin Ducksch (9×); Alexandre Lacazette (8×); Harry Kane (8×); Ivan Toney (7×).

Residual dominan-absen per musim (deskriptif, tanpa gerbang):

| Musim | n | Rata-rata residual [IK 95%] | Kekurangan agregat |
|---|---|---|---|
| 2022/23 | 92 | -0.404 [-0.810, +0.002] | -9.3% |
| 2023/24 | 83 | +0.464 [-0.027, +0.956] | +10.2% |
| 2024/25 | 32 | +1.528 [+0.755, +2.301] | +30.4% |
| 2025/26 | 10 | -0.099 [-0.918, +0.720] | -2.1% |

Residual dominan-absen per divisi (deskriptif, tanpa gerbang):

| Divisi | n | Rata-rata residual [IK 95%] | Kekurangan agregat |
|---|---|---|---|
| E0 | 56 | +0.428 [-0.219, +1.076] | +9.1% |
| D1 | 27 | +0.693 [+0.012, +1.375] | +15.4% |
| I1 | 21 | +0.072 [-0.766, +0.910] | +1.6% |
| SP1 | 38 | -0.290 [-0.946, +0.365] | -7.3% |
| F1 | 75 | +0.214 [-0.298, +0.727] | +4.5% |

### Pengukuran sekunder

Tidak dijalankan — syaratnya (efek primer nyata pada ambang 25% menurut aturan terkunci) tidak terpenuhi.

## Catatan metode

- Porsi trailing memakai jendela expanding tanpa decay (praregistrasi) — berbeda dari V8 yang memakai decay 365 hari. Definisi absen juga lebih ketat dari V8: V8 menghitung 'tidak menjadi starter'; di sini pemain pengganti yang masuk dihitung TAMPIL, jadi 'absen' berarti benar-benar tidak bermain semenit pun.
- Ekspektasi v5 untuk 2022/23 berasal dari pass berjadwal tuning dan untuk 2023/24–2025/26 dari pass berjadwal eval, meniru V8 persis; kedua jangkar reproduksi v5 cocok (lihat Validitas run).
- Satu-satunya informasi hari-laga yang dipakai adalah daftar tampil/tidak tampilnya pemain — persis yang publik ~1 jam sebelum kickoff, titik keputusan JIT yang dinilai. Shotmap laga itu sendiri hanya memperbarui keadaan trailing SESUDAH laganya dinilai.
- Tidak ada odds: akurasi prediksi saja, bukan nilai taruhan.
- Waktu jalan skrip: 415 detik.
