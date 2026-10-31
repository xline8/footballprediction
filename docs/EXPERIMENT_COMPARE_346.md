# Perbandingan rekomendasi #3, #6, dan #4

Branch ini menggabungkan tiga challenger agar dapat dibandingkan dari satu
perintah:

```powershell
python experiments\compare_recommendations_346.py
```

Holdout DC yang sama untuk semua varian Dixon–Coles adalah musim 2021/22–
2025/26 (8.908 pertandingan), dengan `native_priority` xG dan monthly
walk-forward. Bobot #3 dipilih pada validasi 2019/20–2020/21; pooling #6
menggunakan `k_team=5` yang juga dipilih pada validasi.

## Hasil

| Model | Log loss | Brier | RPS | N |
|---|---:|---:|---:|---:|
| DC baseline 50/50 | 0,986732 | 0,587931 | 0,200304 | 8.908 |
| #3 goal–xG global 75% | 0,986305 | 0,587636 | 0,200156 | 8.908 |
| #3 goal–xG league-shrunk | **0,986241** | **0,587588** | **0,200143** | 8.908 |
| #6 hierarchical pooling | 0,986268 | 0,587676 | 0,200198 | 8.908 |

Rekomendasi #4 adalah challenger T3, bukan pengganti langsung DC. Karena itu ia
dibandingkan dengan T3 baseline pada holdout yang sama:

| Model T3 | Log loss | Brier | Accuracy | N |
|---|---:|---:|---:|---:|
| T3 baseline | 0,989870 | 0,589785 | 52,57% | 8.908 |
| T3 + shots/SOT + proxy xG | **0,989007** | **0,589238** | 52,51% | 8.908 |

## Keputusan

Ketiga challenger sudah diimplementasikan di branch ini, tetapi tidak ada yang
menjadi default produksi. Untuk eksperimen lanjutan, #3 league-shrunk adalah
kandidat DC teratas; #6 sangat dekat; #4 memperbaiki proper scoring T3 namun
sedikit menurunkan accuracy.
