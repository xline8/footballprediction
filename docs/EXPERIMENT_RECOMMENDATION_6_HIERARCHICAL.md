# Eksperimen rekomendasi #6 — hierarchical partial pooling

Runner:

```powershell
python experiments\experiment_recommendation_6_hierarchical.py
```

Setiap bulan, Dixon–Coles di-fit memakai data sebelum bulan test. Parameter
attack/defence tim lalu di-shrink menuju mean divisi dan mean global; home
advantage juga di-shrink ke mean global. Nilai `k_team` dipilih pada validasi
2019/20–2020/21 dan dibekukan untuk holdout 2021/22–2025/26.

Validasi memilih `k_team=5`:

| k_team | Log loss validasi | Brier validasi |
|---:|---:|---:|
| 5 | 0,990442 | 0,590173 |
| 15 | 0,992876 | 0,591823 |
| 30 | 0,997603 | 0,595078 |

| Varian holdout | N | Log loss | Brier | RPS |
|---|---:|---:|---:|---:|
| Weighted DC 50/50 | 8.908 | 0,986732 | 0,587931 | 0,200304 |
| Hierarchical pooling | 8.908 | **0,986268** | **0,587676** | **0,200198** |

## Keputusan

Partial pooling memberi peningkatan kecil dan konsisten pada holdout. Branch ini
menyimpan challenger dan protokolnya, tetapi belum mengubah default produksi;
perlu paired block bootstrap dan pemeriksaan khusus tim promosi sebelum
dipromosikan.
