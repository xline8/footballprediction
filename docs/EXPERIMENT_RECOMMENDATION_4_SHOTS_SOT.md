# Eksperimen rekomendasi #4 — shots dan shots-on-target

Runner:

```powershell
python experiments\experiment_recommendation_4_shots_sot.py
```

Fitur dibangun dari `HS/AS/HST/AST` dengan rolling window lima pertandingan,
shrink menuju rata-rata liga, dan kombinasi attack/defence lawan. Semua fixture
pada tanggal yang sama dinilai lebih dulu, baru state tim diperbarui. Jadi fitur
tidak memakai statistik pertandingan yang sedang diprediksi.

Selain fitur rolling, runner melatih ridge proxy-xG pada pertandingan historis
yang memiliki label xG. Koefisien proxy selalu di-fit ulang hanya dari window
training sebelum bulan test.

| Varian | N | Log loss | Brier | Accuracy |
|---|---:|---:|---:|---:|
| T3 baseline | 12.459 | 0,993694 | 0,592011 | 52,21% |
| + shots/SOT + proxy xG | 12.459 | **0,992805** | **0,591291** | **52,28%** |

## Keputusan

Pada sampel walk-forward ini, fitur shots/SOT memberi peningkatan kecil pada
semua metrik utama. Ini masih challenger—belum diaktifkan ke produksi—karena
coverage historis dan validasi lintas musim perlu dipantau lebih lama.
