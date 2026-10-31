# Eksperimen rekomendasi #2 — meta-model 17 fitur

Pertanyaan: apakah jalur meta-model produksi dapat direproduksi secara
leak-free, dan apakah missingness Pinnacle perlu dipisahkan dari nilai netral?

Perintah:

```powershell
python experiments\experiment_recommendation_2_meta17.py
```

Protokol menggunakan `records_cache.jsonl`, join historis ke
`all_matches_enriched.csv`, multinomial logistic numpy yang sama dengan jalur
produksi, dan expanding-window walk-forward per bulan. Batas minimum training
adalah 1.500 pertandingan. Tidak ada file produksi yang ditulis.

| Varian | Fitur | N | Log loss | Brier | Accuracy | Macro-F1 |
|---|---:|---:|---:|---:|---:|---:|
| legacy17 | 9 logit + dev Pinnacle + fair Pinnacle + midweek; PS kosong diimputasi B365 | 66,754 | 1.00111 | 0.59846 | 50.38% | 0.3771 |
| aware19 | legacy17 tanpa imputasi + 2 indikator missingness | 66,754 | 1.00147 | 0.59869 | 50.33% | 0.3774 |

Join mencakup 57.153 baris dan 51.237 baris dengan tiga harga Pinnacle
lengkap. Varian `legacy17` menang tipis pada proper scoring; indikator
missingness tidak otomatis menjadi peningkatan. Namun, eksperimen ini
menunjukkan jalur 17 fitur dapat direproduksi dengan nama kolom Pinnacle lama
(`PS*`) dan baru (`PP*`) ditangani oleh pipeline data.

## Keputusan

Belum mengubah default produksi. `legacy17` adalah kandidat baseline meta yang
lebih kuat, tetapi perbedaannya kecil dan belum diuji dengan paired block
bootstrap. Varian `aware19` disimpan sebagai challenger, bukan dipromosikan.
