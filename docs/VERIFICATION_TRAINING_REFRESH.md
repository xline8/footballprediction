# Verifikasi — Alur Data Hasil & Data Latih

Repo `xline8/footballprediction`. Dua perbaikan, diukur di mesin lokal
2026-10-29. **Tidak ada panggilan API-Football baru** untuk hasil/histori
(grep diff: 0).

---

## Masalah 1 — hasil kemarin di `ta/results.csv` lengkap tanpa intervensi manual

Perbaikan: `run_daily_shadow.py` kini menjalankan
`ta_scrape.py <kemarin> <H-2> --fresh` sebelum grading. `--fresh` memaksa
fetch jaring (cache halaman tanggal 20 menit dilewati); kegagalan jaringan
dicatat sebagai warning, bukan menggagalkan pipeline.

| metrik | sebelum | sesudah |
|---|---|---|
| `ta/results.csv` baris | 1.327 | **1.500** (+173) |
| hasil 2026-10-28 | — | **175** (semua status FT) |
| hasil 2026-10-27 | — | 127 (refresh net) |

Run: `ta_scrape.py 2026-10-28 2026-10-27 --fresh [FRESH]` → 322 laga,
snapshot +191, hasil +173.

---

## Masalah 2 — data latih bertambah

Perbaikan: `step_refresh_training_data` di `pipeline_orchestrator.py`,
dijalankan sebelum `step_fit_models` pada jalur `--run-all`. Melakukan:
unduh CSV football-data.co.uk **musim berjalan saja** (2627, 21 divisi,
`force=True` agar re-unduh walau file ada) → `prepare` → `clean` →
segarkan dump musim Understat via `getLeagueData` → validasi+backup →
rebuild `records_cache` bila data berubah.

| metrik | sebelum | sesudah |
|---|---|---|
| `all_matches_clean.csv` total baris | 70.425 | **70.800** (+375) |
| baris musim 2627 | 1.596 | **1.971** (+375) |
| tanggal maksimum (global) | 2026-10-14 | **2026-10-26** |
| `records_cache.jsonl` | (mode blend) | **69.138** records, direbuild, stamp data baru |

Unduh musim berjalan: 21/21 file OK (E0..G1). Dump xG Understat: EPL 380,
La_liga 380, Bundesliga 306, Serie_A 380, Ligue_1 306.

Backup bertimestamp dibuat sebelum menimpa (`*.bak-*`); validasi total baris &
baris musim berjalan tidak menurun (lulus, 0 pelanggaran clean); rollback
otomatis bila gagal. `test_core.py` → **SEMUA TES LULUS**.

### Catatan keterbatasan sumber (jujur)
football-data.co.uk CSV musim 2627 saat ini baru memuat laga s/d **25–26 Okt**;
laga 28 Okt (Serie A, dll.) belum dipublikasi di file musim berjalan situs
tersebut (lag sumber ~2–3 hari). Karena keputusan user = "tanpa API-Football
untuk hasil", laga itu akan terserap otomatis pada run berikutnya saat
football-data menerbitkannya. Hasil 28 Okt sudah tersedia via jalur terpisah
(tipsterarea, 175 FT di `ta/results.csv`) untuk grading piala/bucket terpisah.

---

## Guardrail

- Data piala (EFL Cup/DFB Pokal) **tidak masuk** data latih: file liga
  (`all_matches_clean.csv`) hanya dari CSV divisi football-data.co.uk
  (E0..G1, tanpa piala); hasil piala tetap grading terpisah via tipsterarea.
- File prediksi liga tidak menyentuh piala (perilaku `predict_*` tidak berubah).
- File runtime (hasil scrape, CSV regenerasi, backup bertimestamp) tidak ikut
  commit: `*.csv`, `*.bak-*`, dan `raw/` di-ignore.
