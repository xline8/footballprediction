# Verifikasi: Orkestrasi Markets Tipsterarea + Join Odds + Grading Piala + Arsip

Tanggal laporan: 2026-10-29. Cabang kerja: baru (belum merge). Semua angka
di atas data lokal saat penulisan; Analis Handal dipersilakan re-run perintah
di bawah untuk verifikasi mandiri.

Ringkasan: **4 dari 5 pekerjaan selesai + 1 finding-stop (corner tipsterarea).**

| Pekerjaan | Status | Bukti |
|---|---|---|
| 1 Markets phase di `run_daily_shadow.py` | ✅ | 26 fixture model, sync +445 harga pasar |
| 2 `market_compare.csv` join odds | ✅ | 26 fixture × 16 baris = 416; Everton-Newcastle terisi |
| 3 Grading corner dari tipsterarea | ⛔ STOP (finding) | halaman FT/laga tanpa stat corner |
| 4 Arsip snapshot harian | ✅ | `archive/2026-10-29/` 6 file, idempoten |
| 5 Pick piala → bucket kompetisi ledger | ✅ | EFL n=0→5, DFB n=0→7 |

---

## Pekerjaan 3 — Finding: corner TIDAK tersedia di tipsterarea (STOP)

Bukti (cache HTML lokal, halaman FT 2026-10-28):
- `ta/raw/match-952385.html` (Man City 2-2 Brighton), `match-952386.html`
  (Bournemouth 3-0 Aston Villa), `match-952387.html` (Fulham 0-1 Crystal
  Palace), `match-952390.html` (Dynamo Dresden 2-0 Schalke), + halaman tanggal
  `ta/raw/date-2026-10-28.html`.

Grep case-insensitive per halaman:

| term | match-952385 | match-952386 | match-952387 | match-952390 | date-28/10 |
|---|---|---|---|---|---|
| corner | 0 | 0 | 0 | 0 | 0 |
| shots | 0 | 0 | 0 | 0 | 0 |
| possession | 0 | 0 | 0 | 0 | 0 |
| cards | 0 | 0 | 0 | 0 | 0 |

Satu-satunya kata "Stat" di halaman laga adalah tautan ke halaman *tim*
(`/teams/england/manchester-city/...`), bukan statistik laga. **Kesimpulan:
halaman laga maupun tanggal tipsterarea tidak memuat jumlah corner per tim.**
Sesuai instruksi, kami **berhenti di sini** — tidak diam-diam ganti sumber, tanpa
API-Football. Corner *tidak* di-grade dari tipsterarea. Jalur corner yang sudah
ada (`ta_model.grade` memakai `HC`/`AC` dari CSV raw football-data.co.uk)
dibiarkan tidak tersentuh.

Reproduksi: `for f in ta/raw/match-952385.html ta/raw/match-952386.html ta/raw/match-952387.html ta/raw/match-952390.html ta/raw/date-2026-10-28.html; do grep -io "corner" "$f" | wc -l; done`

---

## Pekerjaan 1 — Markets phase di daily flow

`run_daily_shadow.py` kini memiliki langkah `[7/9]` sebelum grading: sync odds
pasar untuk **semua fixture model** (liga TOP5 dari `predictions_upcoming.csv` +
piala dari `predictions_cups_upcoming.csv`), window hari ini..+4, urut kickoff
terdekat. Throttle `market_needs_refresh` (~1,5 jam) diurus `sync_dates`;
gagal jaringan = warning, pipeline lanjut. `parse_match_page` dan schema
`odds_markets_snapshots.csv` tidak diubah.

Uji: 26 model fixture terpilih; `sync_dates(... with_markets=True)` →
`{'snapshots': 862, 'markets': 445, 'results': 21, 'games': 1047}`.

Reproduksi:
```bash
python -c "
from datetime import date,timedelta
from market_orchestration import model_fixture_ids
from ta_scrape import sync_dates
days=[date.today()+timedelta(days=k) for k in range(5)]
r=sync_dates(sorted(set(days)), with_markets=True, market_ids=model_fixture_ids(days) or None, verbose=False)
print(r)"
```

---

## Pekerjaan 2 — `market_compare.csv`

Skema (per fixture model upcoming, window hari ini..+4): satu baris per
pasar/garis/pilihan — `div,date,home,away,game_id,competition,market,line,selection,o_1xbet,o_median,p_implied,n_bookies,captured_at`.

- `o_1xbet`: harga terakhir **1xbet** pra-laga.
- `o_median`: median antar bandar (per bandar diambil harga terakhir dari
  semua snapshot; snapshot parsial tidak menghilangkan bandar lain).
- `p_implied`: prob implied **ternormalisasi proporsional** (jumlah = 1),
  mengikuti konvensi `ta_model.market_implied`.
- Snapshot/fixture tanpa harga → kolom kosong (tidak difabrikasi); fixture
  tanpa `game_id` tak ikut (dicatat, bukan gagal).

Coverage: 26 fixture model → 416 baris. Sampel **Everton vs Newcastle**
(952547, EFL Cup, 2026-10-29):

| market | line | selection | o_1xbet | o_median | p_implied | n_bookies |
|---|---|---|---|---|---|---|
| 1X2 | | 1 | 2.31 | 2.28 | 0.4163 | 5 |
| 1X2 | | X | 3.42 | 3.42 | 0.2775 | 5 |
| 1X2 | | 2 | 3.17 | 3.10 | 0.3062 | 5 |
| DC | | 1X | 1.38 | 1.38 | 0.3420 | 5 |
| DC | | 12 | 1.33 | 1.29 | 0.3658 | 4 |
| DC | | X2 | 1.66 | 1.615 | 0.2922 | 4 |
| BTS | | Yes | 1.63 | 1.60 | 0.5756 | 5 |
| BTS | | No | 2.17 | 2.17 | 0.4244 | 5 |

Referensi kutipan prompt (1XBET 2.33/3.46/3.22, DC 1.38/1.34/1.66, BTS Yes
1.63) bergeser ke snapshot terakhir (2.31/3.42/3.17, DC 1.38/1.33/1.66, BTS
Yes 1.63) — sesuai catatan prompt, angka sesuai snapshot terkini.

Reproduksi: `python -m market_orchestration --market-compare`

---

## Pekerjaan 4 — Arsip snapshot harian

`archive/2026-10-29/` berisi 6 file: `predictions_upcoming.csv`,
`predictions_corners_upcoming.csv`, `predictions_cups_upcoming.csv`,
`predictions_corners_cups.csv`, `best_picks_today.csv`, `market_compare.csv`.
Idempoten per tanggal (re-run menimpa file tanggal sama, tanpa duplikasi).
`archive/` ditambahkan ke `.gitignore` (runtime artifact, tidak dikomit).

Reproduksi: `python -m market_orchestration --archive`

---

## Pekerjaan 5 — Pick piala → bucket kompetisi ledger

`sync_cup_picks_to_ledger()` membaca `best_picks_today.csv` (kini + arsip)
ber-label kompetisi, memetakan ke `game_id` (league `England - EFL Cup` /
`Germany - Cup Germany` + nama ternormalisasi), mengambil odds pra-laga
terakhir untuk pasar/garis/pilihan, lalu menulis ke `ledger/picks.jsonl`
dengan `competition="EFL Cup"/"DFB Pokal"`. Hanya pasar yang bisa di-settle
`score_ledger` (1X2/OU) yang dimasukkan; tanpa harga → dilewati.

**Sebelum** (ledger_summary.json): EFL Cup n=0, DFB Pokal n=0.

**Sesudah** (inject 12 pick → `python score_ledger.py`):

| kompetisi | n | profit | ROI | markets |
|---|---|---|---|---|
| EFL Cup | 5 | -1.44 | -28.8% | OU n=5 |
| DFB Pokal | 7 | -3.84 | -54.9% | OU n=7 |

Ledger: picks 276 → 288, graded 276 → 288, pending 0. Idempoten (re-inject =
0).

Catatan terbatas: CLV cup kosong (`clv_coverage=0`) karena proxy close yang
tersedia (`odds_1x2_snapshots.csv`) hanya 1X2, sementara pick cup ini pasar OU
— konsisten dengan desain `_cup_close_proxy` yang sudah ada. ROI piala terpisah
dari liga (semanthics tidak berubah).

Reproduksi:
```bash
python -c "from market_orchestration import sync_cup_picks_to_ledger; print(sync_cup_picks_to_ledger())"
python score_ledger.py
```

---

## Regresi & kendala

- `python test_core.py` → **SEMUA TES LULUS**.
- `git diff`: `ta_scrape.py` tidak tersentuh; tidak ada pemakaian API-Football
  baru; tidak ada file runtime/arsip/ledger yang dikomit (semua gitignored).
- File sumber berubah: `.gitignore`, `pipeline_orchestrator.py`,
  `run_daily_shadow.py`, `market_orchestration.py` (baru), + laporan ini.
