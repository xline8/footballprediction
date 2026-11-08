# Audit: kenapa model pintar per babak selalu gagal ujian?

Tanggal: 2026-11-08. Skrip: `run_halves_audit.py` (semua angka di
`halves_audit_quantities.json`, terverifikasi mereproduksi agregat V3
sebelum satu pun angka audit dihitung). Diminta user sesudah produk
porsi-konstan polos dipertahankan tayang: audit kenapa varian
*pintar*-nya yang selalu gagal gerbang.

## Ringkasan (Bahasa Indonesia)

Empat kegagalan tercatat: (1) fit DC khusus per babak kalah dari
porsi konstan di kedua babak; (2) koreksi bentuk V2 (rho per babak,
overdispersi NB) ter-fit ke hampir nol dan menggeser kalibrasi ke
arah yang salah; (3) pemenang tuning V3 (skala per babak 1,046)
melewati gerbang tuning lalu gagal validasi babak 1 (+2,24pp);
(4) porsi SOT termodel V9 mengalahkan porsi trailing naif tim tetapi
kalah dari konstanta beku.

Audit ini mengukur lima kandidat penyebab. Putusannya:

1. **Tidak ada sinyal porsi per laga untuk dimodelkan — TERBUKTI,
   penyebab utama.** Simpangan baku sejati dari porsi babak-1 antar
   pertandingan terukur **0,0pp** di semua potongan data (total laga,
   kandang, tandang, tim–venue, dan cek silang SOT). Variasi porsi
   yang teramati bahkan sedikit *di bawah* lantai lemparan koin
   murni. Langit-langit oracle-nya nol: model yang tahu porsi sejati
   tiap laga pun tidak akan mengalahkan konstanta, karena tidak ada
   variasi sejati yang bisa diketahui.
2. **Yang berpindah antar-jendela adalah level dan porsi era, bukan
   bentuk distribusi — TERBUKTI, penyebab utama kegagalan koreksi.**
   Porsi babak-1 sejati berkelana antar-musim (SD antar-musim sejati
   ≈ 1,0pp; era 43,1% → 45,4% → 44,2%). Skala tuning V3 ×1,046
   terurai rapi menjadi efek porsi era ×1,026 × efek level ×1,020 —
   dan di jendela validasi keduanya menyusut ke ≈ ×1,00. Koreksi
   yang di-fit pada satu era tiba dalam keadaan sudah basi di era
   berikutnya.
3. **Bentuk distribusi (rho/NB) — GUGUR total.** Rho oracle yang
   di-fit *di dalam* jendela validasi sendiri tetap 0,00/+0,01;
   ukuran NB oracle 6000 (= Poisson); gain oracle NB atas Poisson
   0,00000. Bentuk tidak pernah menjadi masalah — itu sebabnya
   koreksi V2 "ter-fit ke nol": memang tidak ada apa-apa di sana.
4. **Winner's curse klasik — GUGUR sebagai mekanisme utama.**
   Kekurangan babak-1 jendela tuning seragam di ketiga musimnya
   (skala per musim 1,047/1,046/1,045) dan terestimasi presisi
   (bootstrap SD 0,013; P(skala ≤ 1,01) = 0,003). Yang di-fit itu
   nyata *di jendelanya*. Seleksi hanya ikut berperan kecil: kaki
   kalibrasi pemenang lolos dengan margin 0,11pp dan peluang lolos
   bootstrap-nya 63%.
5. **Tidak ada prediktor porsi pra-laga yang stabil — GUGUR
   semua.** Porsi per divisi kalah di luar sampel (−0,00012) dan
   peringkat divisi teracak ulang antar-era; porsi trailing tim yang
   naif kalah −0,0025 dan penyusutan jujurnya memberi bobot nol
   (= konstanta itu sendiri); kemiringan porsi terhadap level
   lambda ≈ 0 di jendela tuning tetapi +0,018/gol di validasi —
   pola spesifik-jendela lagi.

## Rekaman kegagalan yang diaudit

| # | Varian pintar | Hasil vs konstanta polos |
|---|---------------|--------------------------|
| 1 | Fit DC khusus per babak (eksperimen gol 1) | LL 1X2 kalah −0,0018 (babak 1) / −0,0011 (babak 2) |
| 2 | Koreksi rho per babak + NB (V2) | rho ter-fit 0,00/+0,03; NB r=1200 (≈Poisson); kalibrasi bergerak *menjauh*: 1H −2,26→−2,73pp, 2H −3,56→−4,42pp |
| 3 | Skala per babak 1,046/0,999 (V3, satu-satunya lolos tuning) | Validasi babak 1: ΔLL +0,00054 (batas +0,0005), kalibrasi +2,24pp |
| 4 | Porsi SOT termodel (V9) | LL kalah +0,0003 (babak 1) / +0,0012 (babak 2) dari konstanta, walau mengalahkan porsi trailing naif by ~0,018–0,019 |

## A. Lantai noise: berapa banyak variasi porsi yang sungguh nyata?

Metode: dekomposisi varians porsi babak-1 teramati (gol babak-1 /
gol FT, berbobot gol) pada 16.110 laga top-5 2017/18–2025/26 menjadi
varians yang diharapkan dari lemparan koin binomial murni (setiap gol
jatuh ke babak-1 dengan peluang yang sama) dan sisanya = variasi
sejati antar-laga. Divalidasi dengan 500 simulasi nol.

| Potongan | SD teramati | SD lantai koin | SD sejati |
|----------|------------:|---------------:|----------:|
| Total laga (15.051 laga, N≥1) | 27,77pp | 28,75pp | **0,0pp** |
| Total laga, N≥3 saja | 23,51pp | 24,71pp | **0,0pp** |
| Gol kandang saja | 34,85pp | 35,20pp | **0,0pp** |
| Gol tandang saja | 36,83pp | 37,14pp | **0,0pp** |
| Tim–venue (270 unit, ≥30 laga) | 3,61pp | 3,88pp | **0,0pp** |
| Cek silang SOT (15.178 laga) | 16,64pp | 16,85pp | **0,0pp** |

- Cek simulasi: varians teramati 0,0771 vs distribusi nol
  0,0827 ± 0,0007 → **z = −8,0**, persentil 0,0%. Variasi porsi
  teramati bukan hanya "kebanyakan noise" — ia sedikit *di bawah*
  lantai koin murni (rasio varians per strata N turun dari 0,99
  pada N=1 ke 0,82 pada N=7: waktu gol antar-laga sedikit lebih
  teratur daripada proses Poisson — konsisten dengan jeda sesudah
  gol/kickoff ulang; ini interpretasi, bukan syarat putusan).
- Reliabilitas split-half porsi tim–venue: korelasi dua paruh acak
  **r = −0,03** (±0,06) → reliabilitas Spearman–Brown ≈ 0. Tim tidak
  memiliki porsi babak-1 khas yang menetap, pada resolusi 9 musim.
- **Langit-langit oracle** (simulasi pada 5.255 laga validasi,
  porsi laten digambar dengan SD hipotetis, oracle tahu gambarnya;
  kontrol σ=0 menghasilkan 0,000 sesuai harapan):

| SD porsi laten hipotetis | Gain LL oracle babak 1 | babak 2 |
|-------------------------:|-----------------------:|--------:|
| 1pp | 0,0001 | 0,0001 |
| 2pp | 0,0004 | 0,0003 |
| 3pp | 0,0009 | 0,0007 |
| 5pp | 0,0025 | 0,0019 |
| **terukur: 0,0pp** | **0,0000** | **0,0000** |

Bahkan *seandainya* SD sejati 3pp (ditolak data pada >7 SD),
oracle sempurna pun hanya memetik 0,0009 — di bawah margin 0,001
yang dikejar eksperimen 1 dan di dalam derau estimasi model mana
pun. Kerugian tercatat varian pintar (+0,0003 s.d. +0,0018) persis
sebesar biaya varians estimasi yang dibayar untuk mengejar target
yang tidak bergerak.

**Putusan A: TERBUKTI — penyebab utama.** Porsi babak, pada
resolusi data yang ada, adalah konstanta olahraga ini, bukan sifat
pertandingan.

## B. Perkelanaan era: "porsi sejati" itu sendiri berpindah

Porsi babak-1 gabungan per musim (SE ≈ 0,7pp per musim):

| Musim | 17/18 | 18/19 | 19/20 | 20/21 | 21/22 | 22/23 | 23/24 | 24/25 | 25/26 |
|-------|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| Porsi 1H | 43,7% | 41,9% | 43,9% | 45,1% | 45,2% | 45,9% | 44,2% | 45,0% | 43,4% |

- Uji homogenitas: χ² = 23,9 (8 dof), **p = 0,002** — musim-musim
  sungguh berbeda, bukan derau sampling. SD antar-musim teramati
  1,21pp; dikurangi derau sampling → **SD sejati antar-musim
  ≈ 1,0pp**, rentang total 4,0pp.
- Blok era: 2017/18–2019/20 = **43,1%** → 2020/21–2022/23 =
  **45,4%** → 2023/24–2025/26 = **44,2%**. Kenaikan +2,3pp masuk
  blok era 5-pengganti/pandemi, lalu surut −1,2pp pada era waktu
  tambahan panjang pasca-2022 — arahnya cocok dengan perubahan
  rezim yang dikenal, tetapi audit hanya mencatat pergerakannya,
  bukan membuktikan sebab rezimnya.
- Konsekuensi langsung: jendela tuning V3 (porsi aktual 45,42%)
  adalah jendela *menyimpang tinggi*; jendela validasi 44,18%
  kembali ke dekat konstanta beku (44,29% efektif). Koreksi apa pun
  yang menyerap deviasi jendela tuning mewarisi deviasi itu sebagai
  kesalahan di jendela berikutnya.

**Putusan B: TERBUKTI — penyebab utama kegagalan koreksi.** Bukan
hanya level gol yang berkelana (sudah dibuktikan V2/V3); porsinya
sendiri berkelana ±1–2pp antar-era.

## C. Level vs bentuk: oracle pun tidak menemukan bentuk

Cek oracle (di-fit *di dalam* jendela yang sama — diagnosis
in-sample yang disengaja, diberi label, bukan proposal produk),
di bawah harness refit setia-produksi V3:

| Jendela | Babak | Residual mean | Skala optimal tersirat | Rasio dispersi | Rho oracle | NB r oracle | Gain LL NB oracle |
|---------|-------|--------------:|-----------------------:|---------------:|-----------:|------------:|------------------:|
| Tuning | 1H | −0,0557 | 1,0460 | 1,037 | 0,00 | 6000 | 0,00000 |
| Tuning | 2H | +0,0012 | 0,9992 | 0,917 | +0,02 | 6000 | 0,00000 |
| Validasi | 1H | −0,0047 | 1,0038 | 0,956 | 0,00 | 6000 | 0,00000 |
| Validasi | 2H | −0,0122 | 1,0078 | 0,909 | +0,01 | 6000 | 0,00000 |

- Bahkan dengan mengintip jawaban: rho terbaik ≈ 0 dan NB terbaik
  = Poisson murni di keempat sel. Rasio dispersi 0,91–1,04 — total
  per babak justru sedikit *kurang* menyebar dari Poisson
  (sejalan dengan temuan A).
- Rho oracle bahkan tidak memperbaiki kalibrasi in-sample
  (validasi babak 2: −0,71pp dengan rho FT → −1,46pp dengan rho
  oracle). Koreksi bentuk V2 bergerak ke arah salah karena pada
  mean babak (μ ≈ 1,2–1,6) overdispersi pada mean tetap memang
  *menurunkan* P(total ≥ 2) — sudah dicatat V2, kini dikonfirmasi
  dari sisi oracle.
- Pengurai skala V3 (dihitung ulang dari harness): skala tuning
  ×1,0460 = **efek porsi era ×1,0256** (aktual 45,42% vs beku
  efektif 44,29%) × **efek level ×1,0198**. Di validasi:
  ×1,0038 = porsi ×0,9977 × level ×1,0061. Kedua komponen menyusut
  ke ~nol bersamaan.

**Putusan C: bentuk GUGUR total; level (bersama B) TERBUKTI
sebagai pembawa kegagalan.** Semua kegagalan koreksi adalah
kegagalan *mean* antar-jendela, tidak satu pun kegagalan *shape*.

## D. Winner's curse di V3: diuji, dan bukan itu

| Pemeriksaan | Angka |
|-------------|-------|
| Skala babak-1 optimal per musim tuning | 2020/21: 1,0470 · 2021/22: 1,0460 · 2022/23: 1,0449 |
| ΔLL skala global (b) per musim tuning | −0,00083 / −0,00109 / −0,00058 (membaik di ketiganya) |
| Bootstrap skala tuning (B=1000) | mean 1,0459, SD 0,0126, q05–q95 = 1,025–1,067 |
| P(skala* ≤ 1,01) / P(≤ 1,00) | 0,003 / 0,000 |
| P(gain LL tuning ≤ 0) | 0,000 |
| P(kandidat (b) lolos kedua kaki gerbang pada resample tuning) | 0,63 |
| Kesenjangan kebutuhan skala tuning vs validasi | 1,0460 vs 1,0038 = 0,042 ≈ **3,3× SE fit** |
| Kalibrasi validasi pada skala ter-fit | +2,24pp; pada q05 bootstrap (1,025): +1,31pp |
| P(kalibrasi validasi di dalam gerbang ±1pp, dari ketidakpastian fit saja) | **0,011** |

Kekurangan tuning itu *tidak* terkonsentrasi di 1–2 musim dan
*tidak* derau sampling — ia sifat stabil seluruh era tuning.
Kegagalan validasi juga bukan nasib buruk: bahkan ujung bawah
distribusi skala tuning tetap meleset dari gerbang validasi,
karena pusat distribusinya memang milik era lain. Yang tersisa
dari "kutukan pemenang" hanyalah kerapuhan seleksi di kaki
kalibrasi: (b) adalah satu-satunya kandidat yang angka tuning-nya
mendarat di dalam gerbang, dengan margin 0,11pp, dan peluang
lolos bootstrap-nya hanya 63% — memilih "satu-satunya yang lolos"
memperbesar kerapuhan itu, tetapi bukan penyebab utamanya.

**Putusan D: winner's curse klasik GUGUR sebagai mekanisme
utama; kerapuhan seleksi IKUT BERPERAN kecil.** Mekanisme yang
sebenarnya adalah ketidakportabelan antar-era (B + C).

## E. Adakah sinyal per-laga yang stabil? Tidak ada yang selamat

Semua varian dinilai di jendela validasi yang sama, melawan
konstanta venue (produk nol yang tayang; LL gabungan 1H+2H
baseline = 1,09315):

| Kandidat sinyal | Hasil di luar sampel |
|-----------------|----------------------|
| Porsi per divisi (fit era latih) | **−0,00012** (kalah). Porsi latih: SP1 43,3% … E0 45,2%; aktual validasi teracak ulang: D1 46,1% tertinggi, E0 turun ke 43,7% |
| Porsi trailing tim, naif | **−0,00252** (kalah besar — cermin baseline (b) V9) |
| Porsi trailing tim, disusutkan jujur | bobot susut = 0 karena varians sejati terukur 0 → **identik konstanta** (+0,00002, selisih dari pembulatan konstanta gabungan) |
| Porsi sebagai fungsi level lambda FT | slope fit tuning **−0,0008/gol** (≈ nol); slope di validasi +0,018/gol — pola hanya ada di jendela yang tidak dipakai fit. Varian ter-fit: **−0,00074** |
| Pemisahan venue (kandang/tandang) vs satu konstanta global | −0,00001 (tidak bernilai terukur; tidak berbahaya, tetap di produk nol) |

Pola "porsi naik dengan total laga" memang terlihat pada total
*terealisasi* di kedua jendela (slope ≈ +0,007 per gol) — tetapi
itu pengkondisian pada hasil, bukan ramalan: terhadap total
*terprediksi* kemiringannya nol di jendela fit. Ia tidak bisa
dipakai sebelum laga dimulai.

**Putusan E: GUGUR semua.** Tidak ada prediktor porsi pra-laga
yang stabil di antara yang diuji — konsisten penuh dengan A:
yang akan diprediksi memang tidak ada.

## Peringkat penyebab

| Peringkat | Penyebab | Putusan |
|----------:|----------|---------|
| 1 | Lantai noise: variasi porsi sejati per laga = 0,0pp; langit-langit oracle = 0,000 | **TERBUKTI — utama** |
| 2 | Perkelanaan era pada porsi (±1–2pp) + level lambda: koreksi basi saat tiba | **TERBUKTI — utama untuk kegagalan koreksi** |
| 3 | Kerapuhan seleksi di kaki kalibrasi (margin 0,11pp; P(lolos) 63%) | Ikut berperan — kecil |
| 4 | Winner's curse klasik (gain tuning = derau sampling) | **GUGUR** (dibantah bootstrap + keseragaman per musim) |
| 5 | Bentuk distribusi salah (rho/NB) | **GUGUR** (oracle in-sample pun ≈ Poisson, rho ≈ 0) |
| 6 | Sinyal porsi pra-laga yang belum digali (tim/liga/level) | **GUGUR** (semua kalah atau menyusut ke konstanta) |

## Jadi kenapa model pintar selalu gagal

Bahasa sederhananya begini. Membagi gol satu pertandingan ke
babak pertama dan babak kedua itu seperti membagi kue dengan
pisau yang ukurannya sudah tetap: sekitar 44% gol memang jatuh di
babak pertama, dan — ini yang baru terukur tuntas — **potongan itu
praktis tidak berubah dari pertandingan ke pertandingan**. Tidak
ada tim yang "selalu panas di awal", tidak ada laga yang "porsinya
bisa ditebak". Yang terlihat berubah-ubah dari laga ke laga
seluruhnya adalah acak lemparan koin — malah sedikit lebih rapi
dari lemparan koin.

Model pintar gagal bukan karena kurang pintar. Ia gagal karena
disuruh menebak sesuatu yang tidak ada polanya. Setiap
"perbaikan" yang ia pelajari dari data lama sebenarnya adalah
salah satu dari dua hal: sisa acak yang kebetulan tampak rapi di
data lama (lalu hilang di data baru), atau potret satu zaman —
misalnya era 2020–2023 memang sedikit lebih banyak gol babak
pertamanya — yang sudah lewat ketika modelnya dipakai. Sementara
konstanta polos tidak mempelajari apa-apa, jadi tidak ada yang
bisa basi darinya.

Bentuk kurvanya juga tidak pernah salah: di-fit ulang dengan
mengintip jawaban pun, komputer tetap memilih kurva paling
sederhana. Dan pemilihan "yang terbaik dari beberapa kandidat"
ikut memperkeruh sedikit, karena yang terpilih sering hanya yang
paling beruntung di ujian latihan — tetapi audit ini menunjukkan
itu bukan sebab utamanya: kandidat V3 sungguh yang terbaik di
zamannya, hanya saja zamannya berganti.

Satu kalimat: **model pintar selalu gagal karena tidak ada yang
bisa dipintari — porsi babak adalah konstanta, dan satu-satunya
hal yang sungguh bergerak (level gol dan porsi antar-zaman)
bergerak terlalu lambat dan terlalu tak terduga untuk ditangkap
koreksi yang di-fit pada zaman sebelumnya.** Produk polos yang
tayang adalah jawaban yang benar untuk soal ini; pengaman
konfirmasi musim 2026/27 tetap berlaku seperti tercatat di
addendum V3.

## Catatan metode dan batas

- Musim 2026/27 sengaja dikecualikan dari semua pengukuran
  (holdout konfirmasi produk yang tayang; tidak dipakai memilih
  atau menilai apa pun di sini).
- Bagian C adalah diagnosis oracle in-sample yang disengaja dan
  dilabeli: angka-angkanya menguji *apakah bentuk bisa menjadi
  masalah*, bukan mengusulkan produk.
- Simulasi langit-langit A memakai distribusi total Poisson
  (penyederhanaan yang sama dengan kandidat (d) V3); pada
  rho ≈ 0 yang terukur di mana-mana, perbedaan terhadap penskoran
  DC penuh tidak material untuk kesimpulan langit-langit.
- Harness C/D/E meregenerasi prediksi V3 dari mesin produksi dan
  lolos asersi reproduksi agregat V3 (LL dan kalibrasi baseline
  kedua jendela, toleransi 2e-4) sebelum dipakai.
- Satu efek nyata yang *bukan* pra-laga sengaja tidak diadili di
  sini: pengali keadaan turun minum SOT V6 (tertinggal ×1,049) —
  itu informasi dalam-laga, tidak tersedia sebelum kick-off, dan
  tidak mengubah putusan mana pun di audit ini.
