# Eksperimen rekomendasi #3 — bobot gol–xG

Pertanyaan: apakah bobot xG 50% perlu dipelajari secara global atau per liga?

Perintah:

```powershell
python experiments\experiment_recommendation_3_goal_xg.py
```

Eksperimen menggunakan `native_priority` xG, Dixon–Coles bulanan dengan
half-life 270 hari, dan nested walk-forward: grid bobot hanya dipilih pada
musim validasi 2019/20–2020/21, lalu dibekukan pada musim uji 2021/22–2025/26.
Bobot per liga di-shrink ke bobot global dengan prior efektif 1.000 pertandingan.

Validasi memilih bobot global **0,75 xG**. Bobot per liga mentah adalah
E0=0,50, D1=1,00, I1=0,75, SP1=0,75, F1=0,75; setelah shrink menjadi
E0=0,642 dan D1=0,845.

| Varian | N | Log loss | Brier | RPS |
|---|---:|---:|---:|---:|
| Goals (0% xG) | 8.908 | 0,993336 | 0,591757 | 0,202047 |
| Fixed 50/50 | 8.908 | 0,986732 | 0,587931 | 0,200304 |
| Global 75% xG | 8.908 | 0,986305 | 0,587636 | 0,200156 |
| League-shrunk | 8.908 | **0,986241** | **0,587588** | **0,200143** |

## Keputusan

Bobot xG yang dipelajari memberi peningkatan kecil namun konsisten pada musim
uji dan varian league-shrunk menjadi kandidat terbaik. Perubahan produksi belum
diaktifkan otomatis; branch ini hanya menambahkan knob `xg_weight` dan runner
eksperimen. Default tetap 50/50 agar rollback mudah.
