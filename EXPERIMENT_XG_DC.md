# EXPERIMENT_XG_DC — fit Dixon-Coles pada xG vs gol (1X2 out-of-sample)

Eksperimen satu-off. **Produksi tidak diubah** (`model_v2.py` tetap fit pada gol).
Menjawab: apakah mengganti kuantitas observasi DC dari gol ke xG (atau
campuran gol+xG) meningkatkan prediksi 1X2 out-of-sample?

## Step 0 — cakupan xG (audit)

Sumber: `xg_raw/xg_matches.csv` (Understat asli, dibaca via `features._load_xg_map`).
Tidak ada baris mock (`grep -ci mock` = 0) — fallback `_mock_xg` tidak pernah masuk
cache lokal. Join ke `all_matches_clean.csv` pada `(Div, Date, HomeTeam, AwayTeam)`
(team dinormalisasi dua sisi). 16.408 match TOP5; 16.085 ter-join (98,0%).

| league | season | matched | total | % |
|---|---|---|---|---|
| E0 | 2017/18–2025/26 | 380×9 | 380×9 | 100,0 |
| SP1 | 2017/18 | 377 | 380 | 99,2 |
| SP1 | 2018/19–2025/26 | ~378–380 | 380 | 99,5–100 |
| D1 | 2017/18–2025/26 | 305–306 | 306 | 99,7–100 |
| I1 | 2017/18–2025/26 | 378–380 | 380 | 99,5–100 |
| F1 | 2017/18–2025/26 | 279–380 | 279–380 | 97,4–100 |
| semua | 2026/27 (parsial) | 0 | — | 0,0 |

Cakupan asli praktis lengkap untuk 2017/18–2025/26 semua liga. 2026/27 (musim
berjalan, parsial) tanpa xG → **dikecualikan**, tanpa imputasi.

## Varian

Fold identik: walk-forward bulanan (`hl=270`, `freq='m'`, `MAX_TRAIN=4000`,
sama dengan produksi). Test = 2021/22–2025/26. Eksplisit anti-leakage (seluruh
match grup test berada setelah cutoff training).

- **G** gol (kontrol produksi).
- **X** murni xG — rating diz pada xG for/against. **Rho tidak dipilih dari
  "scoreline" xG**; dipakai ulang rho hasil fit gol pada window latih yang sama.
- **B** campuran — observasi = 0,5·gol + 0,5·xG, alpha ditetapkan a priori
  (tidak di-tune pada fold test).

## Hasil — overall (test 2021/22–2025/26, n=8.889)

| variant | logloss | Brier |
|---|---|---|
| G | 0.99304 | 0.59160 |
| X | 0.98678 | 0.58803 |
| B | 0.98624 | 0.58765 |

## Hasil — per liga (logloss)

| league | G | X | B | n |
|---|---|---|---|---|
| E0 | 0.98100 | 0.97736 | 0.97594 | 1900 |
| SP1 | 0.98542 | 0.97728 | 0.97797 | 1897 |
| D1 | 1.00485 | 0.99122 | 0.99273 | 1529 |
| I1 | 0.99354 | 0.99021 | 0.98841 | 1897 |
| F1 | 1.00406 | 1.00037 | 0.99896 | 1666 |

X dan B lebih baik dari G di **kelima** liga.

## Bootstrap berpasangan (10k resample, selisih log-loss per-match vs G)

| pasangan | mean | CI 95% | exclude 0 |
|---|---|---|---|
| X − G | −0.00626 | [−0.00994, −0.00275] | ya |
| B − G | −0.00681 | [−0.00899, −0.00482] | ya |

## Adoption gate (vs G)

| gate | X | B |
|---|---|---|
| logloss overall < G | ya (0.98678 < 0.99304) | ya (0.98624 < 0.99304) |
| CI 95% selisih exclude 0 | ya | ya |
| lebih buruk >0.005 per liga | 0 liga | 0 liga |
| **verdict** | **PASS** | **PASS** |

## Verdict & rekomendasi

Kedua varian **LULUS** gate. Terbaik overall: **B (campuran 0,5 gol + 0,5 xG)** —
logloss terendah (0,98624) dan CI termenyet (−0,00681 [−0,00899, −0,00482]).
X (murni xG) juga lulus dan hampir sama (0,98678).

Rekomendasi produksi: pindahkan fit DC ke **campuran 0,5·gol + 0,5·xG** (B).
Namun ini **eksperimen** — switch produksi tidak diimplementasikan di tugas ini.
Langkah lanjut yang disarankan sebelum go-live: validasi pada fold validasi
(2019/20–2020/21) sebagai konfirmasi, dan periksa efeknya pada pasar turunan
(O/U, BTTS) yang ikut bergeser karena lambda model berubah.

---

# Go-live gates (switch produksi ke B)

`model_v2.py` kini punya flag `DC_FIT_MODE` (`goals`|`blend`, override env
`FOOTBALL_DC_FIT_MODE`). Fit `blend` = observasi 0,5·gol + 0,5·xG bila xG
tersedia (fallback gol bila tidak), rho selalu dipilih pada fit gol window yang
sama. Tiga gate dijalankan sebelum default di-flip; SEMUA lulus.

## Gate A — meta stack (blend vs goals)

Bangun ulang `records_cache.jsonl` (produksi `cache_records`) kedua mode pada
universe identik, refit meta 9-logit walk-forward bulanan, stacked 1X2 log loss.

| mode | stacked LL | n |
|---|---|---|
| goals | 1.00166 | 68.763 |
| blend | 1.00165 | 68.763 |

PASS (blend ≤ goals).

## Gate B — derivatif (G vs B, fold eksperimen 2021/22–2025/26)

Harga O/U 2.5 & BTTS dari matriks scoreline varian masing-masing.

| market | LL goals | LL blend | Δ | Brier goals | Brier blend | n |
|---|---|---|---|---|---|---|
| over 2.5 | 0.68370 | 0.67775 | −0.00595 | 0.24495 | 0.24237 | 8.889 |
| BTTS | 0.69088 | 0.68464 | −0.00624 | 0.24823 | 0.24577 | 8.889 |

PASS (kedua market membaik; tali degradasi > +0.002).

## Gate C — held-out seasons (2017/18–2020/21)

| mode | LL | n |
|---|---|---|
| goals | 1.02333 | 7.196 |
| blend | 0.99300 | 7.196 |

PASS (blend ≤ goals, Δ −0.03034).

## Verdict

Semua gate lulus → default `DC_FIT_MODE` di-flip ke `blend`. Verifikasi
end-to-end: `test_core.py` lulus, pipeline `--run-all` exit 0, step cups 13/13,
records cache direbuild di bawah blend (stamp `records_cache.meta.json` =
`{"dc_fit_mode":"blend"}`).

Runtime gates: ~983s (dua rebuild cache penuh). Runner: `go_live_gates.py`.
