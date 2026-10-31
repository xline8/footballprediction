# Eksperimen rekomendasi #5 — dynamic state-space Dixon–Coles

Runner:

```powershell
python experiments\experiment_recommendation_5_state_space.py
```

Challenger ini memperbarui attack/defence setiap selesai pertandingan memakai
residual Poisson. Semua pertandingan pada tanggal yang sama diprediksi sebelum
state diperbarui. Learning rate dipilih hanya pada 2019/20–2020/21, kemudian
dibekukan untuk holdout 2021/22–2025/26.

Grid validasi `0,01/0,02/0,04/0,08` memilih `0,01`, tetapi filter online
sederhana ini belum mengalahkan Dixon–Coles weighted yang sudah ada:

| Varian | N | Log loss | Brier | RPS |
|---|---:|---:|---:|---:|
| Weighted DC 50/50 | 8.908 | **0,986732** | **0,587931** | **0,200304** |
| Dynamic state-space | 8.908 | 1,181020 | 0,713612 | 0,261965 |

## Keputusan

Eksperimen **ditolak untuk produksi**. Hasil ini bukan bukti bahwa state-space
tidak berguna; implementasi ini baru online residual filter tanpa likelihood
penalized, smoothing, atau estimasi process-noise yang matang. Ia disimpan
sebagai baseline challenger dan titik awal untuk implementasi state-space yang
lebih lengkap.
