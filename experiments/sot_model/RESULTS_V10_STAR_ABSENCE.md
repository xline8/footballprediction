# Model SOT v10 — Uji Absennya Penembak Dominan ("bintang absen") (eksperimen, BUKAN produksi)

## Ringkasan (Bahasa Indonesia)

_(Ringkasan diisi setelah run selesai. Bagian Desain di bawah ini ditulis dan dikunci SEBELUM angka hasil apa pun dihitung — lihat "Praregistrasi".)_

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
