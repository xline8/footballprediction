# Job Harian — football-daily (cron 05:35)

Konteks: proyek bola di PC ini. Modul data = `C:/Users/Arif Wicaksono/football-data`, situs = `C:/Users/Arif Wicaksono/football-site`.

**Aturan mutlak**
- Jangan bertanya; jalan otomatis. Bila satu langkah gagal, catat singkat, lanjut langkah berikutnya.
- DILARANG: mengubah model/config (`model_v2.py`, `v2_config.json`), menjalankan `npx`, mengedit angka manual, memberi saran taruhan/deposit.
- Semua file yang ditulis WAJIB di path absolut seperti di bawah.

## Langkah 1 — refresh CSV football-data (via web_extract; situs memblokir curl/python)
Untuk tiap DIV dalam daftar `E0, SP1, D1, I1, F1`:
1. `web_extract` dengan url: `https://www.football-data.co.uk/mmz4281/2627/<DIV>.csv` dan `char_limit: 400000`.
2. Simpan `content` apa adanya ke `C:/Users/Arif Wicaksono/football-data/raw/<DIV>_2627.csv`.
3. Validasi: content harus berawalan baris header yang mengandung `B365H`; catat tanggal match terakhir file baru.
4. Bila gagal/kosong/aneh: **jangan timpa** file lama; catat gagal.

## Langkah 2 — scrape Understat (browser)
Liga (slug): `EPL, La_liga, Bundesliga, Serie_A, Ligue_1`.
Per slug: buka `https://understat.com/league/<slug>/2026`, tunggu variabel `datesData` dengan polling JS
`(typeof datesData !== 'undefined') ? JSON.stringify(datesData) : 'WAIT'`
maksimal 20 kali dengan jeda 1 detik. Simpan JSON penuh ke `C:/Users/Arif Wicaksono/football-data/xg_raw/<slug>_2026_all.json`.
Tolak menyimpan bila isinya bukan array. Gagal satu liga → catat, lanjut liga berikutnya.

## Langkah 3 — pipeline python (terminal)
Workdir: `C:/Users/Arif Wicaksono/football-data`, urutan:
```
python score_ledger.py
python make_picks.py
python predict_upcoming.py
python C:/Users/Arif Wicaksono/football-site/build_data.py
```
Semua exit code 0 dianggap sukses. Bila ada yang gagal -> catat traceback 1-2 baris.

## Langkah 4 — lapor (Bahasa Indonesia, maks ±12 baris)
- CSV ter-refresh per div + tanggal match terakhir tiap div (harus makin maju tiap hari; 16 Okt 2026 baris terakhir E0 ± 12 Okt).
- Picks baru + total ledger; picks ter-grade baru + hasilnya; bila ada, ROI berjalan per pasar.
- Jumlah fixture 10-hari di jadwal + berapa yang sudah punya harga.
- Status `build_data.py`.
- Semua sukses tanpa picks/grade baru = normal (harga FD belum dibuka), tetap lapor 3-4 baris.
- Tutup dengan kalimat tetap: **"Backtest: ROI negatif vs closing & opening — tetap jangan deposit."**

## PERUBAHAN 17 Okt: cron lama dihapus user; sumber harga baru = Nowgoal via browser
- Cron 05:35 (FD CSV) DIHAPUS oleh user; DAILY_JOB ini tetap jadi kontrak manual.
- Sumber harga baru: https://www.nowgoal25.com/ (redirect live.nowgoal50.com) — 1X2 desimal + AH (format HK).
- Cara tarik: browser ke situs, klik "Show All", jalankan `nowgoal_extract.js` (v2: pre+live+FT skor/HT) di halaman (browser_exec).
  Simpan hasil ke `raw/odds_nowgoal_<YYYYmmdd_HHMM>.csv` (APPEND-ONLY, jangan edit file lama).
- Contoh terkunci 17 Okt 2026 01:28 WIB: 12 match top-5, file odds_nowgoal_20261017_0128.csv,
  edge dihitung vs model v2 — edge tertinggi +37% (Elversberg H) = TANDA BAHAYA, bukan sinyal:
  backtest opening menunjukkan pola edge besar ini kalah (ROI @2% = -13%). Baca verdict JANGAN deposit.
- Alias nama wajib untuk pencocokan: Eintracht Frankfurt->Ein Frankfurt; RCD Espanyol->Espanol;
  SV Elversberg->Elversberg; FC Koln = FC Koln; belum dipetakan = SKIP, jangan menebak.
- Jadwal pertandingan di situs sudah WIB (render layer, app.js toWib +7h).

## CRON AKTIF 17 Okt: odds-snapshot (id dc8a1d8f3827) — tiap 60 menit, hasil deliver=local
- Alur per fire: buka nowgoal25.com -> klik "Show All" -> jalankan nowgoal_extract.js (v2) via browser
  -> simpan raw/_latest_snapshot.json -> python snapshot_to_db.py raw/_latest_snapshot.json
- Output: raw/odds_nowgoal_<ts>.csv (immutable) + raw/odds_timeseries.csv (append) + preview edge vs model (log).
- Job ini TIDAK membuat pick & TIDAK menulis ledger (disiplin). Model/config/html DILARANG disentuh.
- Gagal situs = lapor & berhenti. Cermin (movietime.tv dkk) DILARANG.

## JADWAL TERSAMBUNG 17 Okt (02:3x WIB)
- Baru: build_odds_feed.py -> site/assets/odds-latest.js (window.ODDS_LATEST; harga pre terakhir per fixture, tanda waktu snapshot).
- app.js renderJ memakai ODDS_LATEST dulu, fallback harga lama B365; jadwal.html th jadi "Harga 1X2 (pasar)" + lede jujur (Nowgoal buku Asia, bukan B365).
- ALIAS arah benar: nama PANJANG nowgoal -> nama PENDEK model (Man City, Nott'm Forest, La Coruna, Dortmund, Ath Madrid, dkk.) + jendela tanggal <=1 hari; pasangan salah H privat HUGA dicegah (Fulham-Hull kenyataan MW7).
- Cron dc8a1d8f3827 step 5 = build_odds_feed.py (update prompt 02:3x).
## PICK LAHIR 17 Okt 02:28 WIB (birth_picks.py pertama)
- 8 pick pending (1x2, edge>=2%, harga = snapshot terakhir ber-tanda waktu; idempoten teruji 0 dobel).
- Situs: ledger.html baca assets/ledger-latest.js (window.LEDGER_LATEST) via app.js fallback.
- Cron dc8a1d8f3827 langkah 6 = birth_picks.py.
- Grading pending->win/loss dari skor FT snapshot = INKREMEN BERIKUT (score_ledger adaptasi).
- Parlay terverifikasi jalan (slider 3->5, EV -13,61% -> -21,64%). Keluhan user = cache browser.

## GENERATOR BET SLIP + GRADING FT — 17 Okt (~03:40 WIB)
- `grade_picks.py` masuk cron (langkah 6; lulus dry-run "0 baru" — grading pertama menyusul saat match top-5 selesai).
- Generator bet slip hidup di parlay.html: auto (slider 2-8 leg, pilih keyakinan tertinggi dari 12 fixture berharga) + manual (pilih H/D/A per match); slip = leg + odds gabungan + peluang tembus + payout + EV berlabel warna; tombol Salin slip (clipboard + fallback).
- Cron kini 7 langkah: extract -> snapshot_to_db -> build_odds_feed -> grade_picks -> birth_picks.
- Fix runtime app.js: gLegsV/dLabel tak terdeklarasi (ReferenceError strict-mode mematikan inisialisasi), artefak `void` dibersihkan, DIVN naik ke module scope (dipakai lintas halaman).
- Positioning: "tipster statistik yang jujur" (hero index + footer jadwal/ledger/metodologi/parlay; peringatan backtest tetap tampil).

## REFRESH FIXTURE UNDERSTAT — 17 Okt (~09:45 WIB)
- Temuan Understat: (1) halaman liga kini shell ~18KB tanpa `var *Data` -> pure-python scrape MATI; refresh berikutnya wajib jalur browser (spt nowgoal). (2) Frankfurt-Koln & Deportivo-Levante TIDAK PERNAH ada di Understat sepanjang musim (sudah FT, direkam snapshot) -> SKIP oleh pairing adalah perilaku benar, bkan bolong.
- Skrip baru: refresh_fixtures.py (fetch+backup+diff, fallback disk) & build_appdata.py (bedah "upcoming" dgn jendela 10 hari + hari ini inklusif s.d. 27 Okt; prob pk *_bl bila ada dulu; odds/edge = null -> harga 1X2 situs murni snapshot Nowgoal; backup app-data.prev.js).
- Hasil run: fixture 96 -> 96 (rentang 17..27 Okt, 5 prob pertama identik dgn lama); fixture berharga naik 12 -> 19 (unpriced 84 -> 77) krn snapshot jam-an; ledger 8 -> 14 pick (lahtir otomatis cron 04:09 & 05:11, smua harga pre terekam sblm lahir).
- Catatan kualitas data: 5 baris pre difile timeseries dgn `captured` kosong (x2 Fulham 4.75) - dgn sort captured, baris valid selalu menang (JANGAN etimasi); skema tak diubah.
- PREDICT/UMAM: predict_upcoming.py dengan dump musim penuh menghasilkan 1450 baris (s.d. Mei 2027) - biarkan, situs dibatasi jendela oleh build_appdata.

## REFRESH UNDERSTAT VIA API + CRON LANGKAH-8 — 17 Okt (~11:50 WIB)

**Temuan:** halaman liga Understat = shell (data via XHR), tapi API internal `getLeagueData/{slug}/2026` TERBUKA untuk python murni: 3 header XHR (Referer, X-Requested-With, Accept) + body gzip (cek magic `\x1f\x8b`) → JSON key `dates` (list fixture, bukan `datesData`).
**Hasil:** `refresh_fixtures.py` fetch() diganti ke endpoint tsb — live 5/5 liga (380/380/306/380/306 rows, sumber=understat.com, diff 0). Proxy tiprouter TIDAK diperlukan (blok lama hanya di halaman HTML) — daftar tetap ada bila suatu saat dibutuhkan.
**Cron odds-snapshot (dc8a1d8f3827):** kini 8 langkah — langkah 8 = `refresh_fixtures.py`; bila diff ≠ 0 → `predict_upcoming` → `build_appdata` → `build_odds_feed` (input data saja). Laporan cron kini menyertakan "U: refresh fixture (+N baru)". Verifikasi prompt tersimpan di jobs.json (1.779 chars).
