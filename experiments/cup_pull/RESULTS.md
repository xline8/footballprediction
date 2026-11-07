# Pull Aktual Piala (EFL Cup + DFB Pokal) dari FotMob — Hasil

## Ringkasan (Bahasa Indonesia)

Data aktual piala akhirnya mendarat. Dari 119 laga piala musim 2026/27 yang
ada di daftar fixture TipsterArea (sumber fixture `predict_cups.py`) —
84 EFL Cup dan 35 DFB Pokal, semuanya sudah FT — **117 laga (98,3%) berhasil
dipasangkan ke laga FotMob dan respons matchDetails utuhnya tersimpan** di
gudang `data_enrichment/fotmob_full/` dengan kunci kompetisi baru `EFLCUP`
dan `DFBPOKAL`. Ke-117 laga itu semuanya punya skor akhir DAN jumlah corner
per tim, dan sudah diekstrak ke satu CSV siap-grading:
`data_enrichment/cup_actuals.csv` (117 baris). Prediksi piala sekarang, untuk
pertama kalinya, punya aktual dari sumber independen untuk di-grading
(termasuk corner piala yang selama ini memang tidak pernah di-grading).

Dua laga yang gagal dipasangkan keduanya laga babak pendahuluan
(preliminary round) EFL Cup — Tranmere Rovers v Rochdale (2026-08-01) dan
York City v Crawley (2026-08-03) — yang memang tidak dibawa FotMob di daftar
fixture EFL Cup 2026/27-nya (daftar FotMob mulai dari putaran pertama,
2026-08-06). Bukan kegagalan resolusi nama: tidak ada fixture FotMob dalam
jendela ±1 hari untuk kedua laga itu.

Dua catatan kualitas data yang penting untuk siapa pun yang nanti meng-grading:

1. **Dua baris DFB Pokal berskor "setelah perpanjangan waktu" (AET), bukan
   90 menit.** Waldhof Mannheim v Kaiserslautern (FotMob 0-1, gol menit
   120; TipsterArea mencatat 0-0) dan Hallescher v Schalke 04 (FotMob 2-5;
   2-2 di 90 menit, tiga gol Schalke di perpanjangan waktu; TipsterArea
   2-2). Di luar dua laga ini, skor FotMob cocok persis dengan skor FT
   TipsterArea di 115 dari 117 laga. Karena probabilitas `predict_cups.py`
   adalah probabilitas 90 menit (peluang lolos dihitung terpisah di kolom
   `p_adv_*`), peng-grading harus sadar dua baris ini berisi gol
   perpanjangan waktu.
2. **19 laga ditentukan lewat adu penalti** (15 EFL Cup, 4 DFB Pokal).
   Untuk laga-laga itu skor di CSV adalah skor imbang sebelum adu penalti
   (gol adu penalti TIDAK ditambahkan) — sesuai untuk grading pasar
   90 menit.

Tidak ada file produksi yang diubah, tidak ada kode/perilaku grading yang
disentuh — item ini murni pendaratan data, sesuai mandat audit
`experiments/MODEL_AUDIT_2026-11-07.md` §4 / §2C C-3 (peringkat 6).

## Fixture universe (exact statement)

- Competitions: exactly those `predict_cups.py` predicts —
  `CUP_LEAGUES = {"England - EFL Cup": "EFL Cup", "Germany - Cup Germany":
  "DFB Pokal"}`.
- Set pulled: rows of `ta/fixtures.csv` (the `predict_cups.py` fixture
  source) with those two league strings, season **2026/27**
  (date ≥ 2026-08-01), status **FT** → **119 fixtures (EFL Cup 84,
  DFB Pokal 35)**.
- Past predictions/ledger artifacts checked for additional past cup
  fixtures: `archive/*/predictions_cups_upcoming.csv`,
  `archive/*/predictions_corners_cups.csv`,
  `predictions_cups_upcoming.csv`, `predictions_corners_cups.csv`,
  `ledger/picks.jsonl`. They contain exactly **one** predicted cup tie —
  Everton v Newcastle (EFL Cup, 2026-10-29; archive snapshot 2026-10-29
  and the ledger's only cup pick) — which is already inside the 119, so
  the union adds **0** fixtures.
- Explicitly out of scope: the 2025/26 TA cup history (140 FT ties in
  `ta/fixtures.csv`), FotMob-only fixtures TipsterArea does not list
  (e.g. DFB Pokal R1 ties vs lower-league clubs, 13 finished ties), and
  unplayed future ties (Dec 2026 EFL quarter-finals / DFB round of 16,
  present in FotMob payloads but not in TA and without actuals).

## Competition / key naming

| Competition (CSV value) | Store key (directory) | TA league string | FotMob league id | ccode3 |
|---|---|---|---|---|
| EFL Cup | `EFLCUP` | `England - EFL Cup` | 133 | ENG |
| DFB Pokal | `DFBPOKAL` | `Germany - Cup Germany` | 209 | GER |

Store layout: `data_enrichment/fotmob_full/<KEY>/2026-27/<fotmob_id>.json`
(season directory with a dash, same convention as the league store; the
store is gitignored — expected). CSV naming: `home`/`away` are the
TipsterArea names verbatim (the system's own naming, joins directly
against `predict_cups.py` outputs and `ta/results.csv`); `season` uses the
repo convention `2026/27`.

## Coverage

| Competition | Fixtures attempted | Matched to FotMob | Responses stored | Rows with score | Rows with corners | Unmatched |
|---|---:|---:|---:|---:|---:|---:|
| EFL Cup | 84 | 82 | 82 | 82 | 82 | 2 |
| DFB Pokal | 35 | 35 | 35 | 35 | 35 | 0 |
| **Total** | **119** | **117** | **117** | **117** | **117** | **2** |

Fetch health: 117 fetched over HTTP, 0 reused, 0 errors, 0 provider stops
(12 workers, zero delay — the established FotMob pacing). Matching used
`fixture_map_fixed` (same-date, score ≥ 1.60, ambiguity margin 0.10);
the ±1-day fallback pass was needed 0 times.

### Unmatched fixtures

| Date | Fixture | Reason |
|---|---|---|
| 2026-08-01 | tranmere rovers v rochdale (EFL Cup, TA game_id 937420) | Preliminary-round tie; absent from FotMob's EFL Cup 2026/27 fixture list — no FotMob fixture within ±1 day |
| 2026-08-03 | york city v crawley (EFL Cup, TA game_id 937700) | Preliminary-round tie; absent from FotMob's EFL Cup 2026/27 fixture list — no FotMob fixture within ±1 day |

### Score cross-check vs TipsterArea

FotMob FT score vs `ta/fixtures.csv` FT score: **115/117 exact**. The two
exceptions are the AET ties documented in the summary above (Waldhof
Mannheim v Kaiserslautern, Hallescher v Schalke 04) — FotMob reports the
after-extra-time score, TipsterArea the 90-minute score.

Outcome breakdown of the 117 stored ties (from `header.status`): decided
in 90 minutes 96, after extra time 2 (both DFB Pokal), on penalties 19
(15 EFL Cup + 4 DFB Pokal; CSV score = pre-shootout drawn score).

## Files

- `experiments/cup_pull/pull_cup_fotmob.py` — universe build, FotMob
  resolution (league payloads + `fixture_map_fixed` + ±1-day fallback),
  parallel matchDetails pull into the store layout.
- `experiments/cup_pull/extract_cup_actuals.py` — extraction from stored
  responses to the grading CSV + TA score cross-check.
- `experiments/cup_pull/pull_report.json` — full matched mapping,
  unmatched list with reasons, fetch stats.
- `experiments/cup_pull/extract_summary.json` — extraction counts +
  cross-check mismatches.
- `data_enrichment/fotmob_full/EFLCUP/2026-27/*.json` — 82 responses
  (gitignored store).
- `data_enrichment/fotmob_full/DFBPOKAL/2026-27/*.json` — 35 responses
  (gitignored store).
- `data_enrichment/cup_actuals.csv` — 117 rows; columns `competition,
  season, date, home, away, fotmob_match_id, goals_home, goals_away,
  corners_home, corners_away`. No fabricated values: every stored
  response carried both a score and a corners pair, so no blank cells
  occur in this run.

## Rerun

```bash
.venv/bin/python experiments/cup_pull/pull_cup_fotmob.py     # idempotent; stored files are reused
.venv/bin/python experiments/cup_pull/extract_cup_actuals.py
```

`--seasons 2025/26` on the pull script would extend the universe to the
older TA cup history if a future decision wants it; it was not run.
