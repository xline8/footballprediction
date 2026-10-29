# Verifikasi: Grading Harian untuk Pick Teraman & Rekomendasi (Kalibrasi)

Tanggal laporan: 2026-10-29. Cabang: `feat/grading-rekomendasi-kalibrasi`
(commit `9a2b8af`). Analis Handal dipersilakan re-run perintah di bawah.

## Perubahan

| File | Status | Isi |
|---|---|---|
| `grade_recommendations.py` | baru | modul grading (settlement murni + idempoten) |
| `run_daily_shadow.py` | diubah | langkah `[8c/9]` (isolasi try/except) sebelum arsip |
| `tests/test_units.py` | diubah | 12 test unit baru (23 total) |
| `README.md` | diubah | paragraf di Live shadow tracker |

Tanpa perubahan pada `model_v2.py`, `ta_model.py`, `best_picks.py`,
`slip_recommender.py`, `score_ledger.py`, atau bucket ledger policy-engine.

## Output

- `ledger/daily_pick_grades.jsonl` — 25 baris: 13 hit, 4 lose, 8 pending,
  0 push, 0 ungratefulable.
- `ledger/calibration_summary.json` — potongan:

```json
{
  "overall": { "n": 17, "mean_p": 0.9356, "hit_rate": 0.7647, "diff": -0.1709, "push": 0 },
  "by_product": { "pick_teraman": { "leg": { "n": 17, "mean_p": 0.9356, "hit_rate": 0.7647 } },
                   "slip2": { "leg": {"n":0}, "unit": {"n":0} },
                   "slip10": { "leg": {"n":0}, "unit": {"n":0} } },
  "by_market": { "DC": { "n": 4, "hit_rate": 0.5 }, "OU": { "n": 13, "hit_rate": 0.8462 } },
  "brier_pick_teraman": 0.1905,
  "pending": { "count": 8, "reasons": { "no_result_yet": 6, "legs_pending": 2 } },
  "ungradeable": { "count": 0, "reasons": {} }
}
```

Slip legs (`2026-10-29`) belum FT saat penulisan → pending; unit slip ikut
pending (`legs_pending`). Semua pick `best_picks_today.csv` tanggal
`2026-10-28` sudah FT di `ta/results.csv` → final.

## Perintah verifikasi

```bash
python grade_recommendations.py            # run 1: 25 baris
python grade_recommendations.py            # run 2: baris_baru/diperbarui=0, 25 baris (idempoten)
python tests/test_units.py                 # 23 unit tests passed
python test_core.py                        # SEMUA TES LULUS
python run_daily_shadow.py                 # EXIT=0, langkah [8c/9] aktif
```

## Kriteria penerimaan

1. ✅ standalone + pipeline penuh exit 0 dengan langkah aktif
2. ✅ run vs arsip `2026-10-29` → pending terisi tanpa error, summary terbit
3. ✅ idempoten: dua run -> jumlah baris final tidak berubah (25), `changed=0`
4. ✅ test unit lulus; `test_core.py` lulus
5. ✅ hanya `grade_recommendations.py` baru + langkah di `run_daily_shadow.py`
   + test + README; tanpa sentuhan model/pick/ledger

## Penyimpangan & catatan

- **Arsip 2026-10-29 awal hanya 7 dari 9 file** — `recommended_single.csv` dan
  `recommended_slip10.csv` belum ada (produk slip direfaktor setelah arsip
  tanggal itu dibuat). Produk ketiga di-regenerasi (`slip_recommender.recommend`)
  dan `archive_snapshots` dijalankan ulang sehingga arsip menjadi 9 file.
- **Posisi langkah di `8c/9` (sebelum arsip), bukan sesudah grading ledger.**
  Grading ledger (`resolve_and_monitor`) kini berjalan setelah arsip; grading
  rekomendasi hanya butuh hasil (`ta/results.csv` setelah `[6/7]`) dan arsip
  tanggal sebelumnya, jadi "sebelum langkah arsip" dipenuhi dan aman.
  `[8c/9]` menilai arsip yang sudah ada di disk (hari-hari sebelumnya); arsip
  hari ini dibuat setelahnya di `[9/9]`.
- **Pita probabilitas** diberi catch-all `<0.50` agar leg di bawah lantai
  0.50 (single/slip10 punya lantai 0.40/0.35) tidak dibuang dari `by_band`.
- **Unit slip**: `p_model` = joint probability, `odds` = total odds (dari
  kolom `slip_joint_prob`/`slip_total_odds`).
- **Brier pick_teraman** dihitung atas leg final non-push.
