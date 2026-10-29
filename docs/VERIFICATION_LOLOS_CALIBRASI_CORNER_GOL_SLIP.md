# Verifikasi: Probabilitas Lolos Piala + Kalibrasi Corner Liga + Total Gol Piala + Slip Odds

Tanggal laporan: 2026-10-29. Cabang: `feat/lolos-calibrasi-corner-gol-slip` (4
commit terpisah). Semua angka di atas data lokal saat penulisan; Analis Handal
dipersilakan re-run perintah di bawah untuk verifikasi mandiri.

Ringkasan: **4 dari 4 pekerjaan selesai. Gate koreksi corner TIDAK terpenuhi
→ model corner tidak diubah (hanya lapor).**

| Pekerjaan | Commit | Status | Bukti |
|---|---|---|---|
| 1 p_adv lolos piala | `a51a88c` | ✅ | sum=1, monotonicity, Man City/Liverpool/Bayern |
| 2 Kalibrasi corner liga | `4717f62` | ✅ (lapor, tanpa ubah) | gate tidak terpenuhi |
| 3 Total gol piala per kompetisi | `0597151` | ✅ | 272 hasil FT, anchor ke laju cup |
| 4 Rekomendasi slip ±2.0 | `c8d2c83` | ✅ | 2 kaki, total 1.915, in_band |

---

## Pekerjaan 1 — p_adv lolos piala (single-leg)

`predict_cups.py` + kolom `p_adv_h`/`p_adv_a` di `predictions_cups_upcoming.csv`.
Formula: `p_adv_h = ph + pd·q_h`, dengan `q_h = P(menang ET) + P(seri ET)·q_pens_h`,
`λ_ET = λ × 30/90`, `q_pens_h = ph/(ph+pa)` (fallback 0.5). Hanya untuk format
satu leg (EFL Cup & DFB Pokal kini begitu); format dua leg -> kolom kosong.

Sampel ronde 2026-10-28 (di-regenerasi dari rating saat ini; angka tidak harus
identik dengan laporan lama):

| laga | ph | pd | pa | p_adv_h | p_adv_a | sum | p_adv_h≥ph |
|---|---|---|---|---|---|---|---|
| Man City v Brighton | 0.5248 | 0.2506 | 0.2246 | 0.6938 | 0.3062 | 1.0000000 | ✅ |
| Liverpool v Chelsea | 0.4947 | 0.2562 | 0.2491 | 0.6595 | 0.3405 | 1.0000000 | ✅ |
| Bayern v Magdeburg | 0.7161 | 0.1841 | 0.0998 | 0.8704 | 0.1296 | 1.0000000 | ✅ |

Catatan jujur: **Bayern p_adv_h = 0.8704, bukan >0.95.** Ini batas struktural,
bukan bug: `p_adv_h = ph + pd·q_h ≤ ph + pd = 1 − pa = 0.90` untuk fixture ini
(pa=0.0998). Ambang 0.95 mengandaikan rating jauh lebih timpang daripada yang
dihasilkan anchor λ (total dinormalisasi ~2.7). p_adv_h>0.5 dan >ph tetap
terpenuhi.

Reproduksi:
```python
import predict_cups as pc
from datetime import date
from model_v2 import DC
m=pc._load_matches(); td=pc._team_div_map(m); today=date.today()
for h,a in [("man city","brighton"),("liverpool","chelsea"),("bayern munich","magdeburg")]:
    hd,ad=td[pc._norm(h)],td[pc._norm(a)]
    lh,la=pc.cross_lambdas(m,hd,ad,pc._norm(h),pc._norm(a),today)
    pr=DC().probs(lh,la)
    print(h, pc.p_adv(pr["ph"],pr["pd"],pr["pa"],lh,la))
```

---

## Pekerjaan 2 — Kalibrasi corner liga (gate: TIDAK terpenuhi)

`experiment_eval_corners.py`: walk-forward per musim 2019/20–2025/26 dari
HC/AC `all_matches_clean.csv`, model produksi (gamma=0.15, r=1.1868), per divisi
+ pooled.

**Bias (mean mu−aktual) per divisi, pooled:** E0 −0.033, D1 −0.042, I1 +0.232,
SP1 −0.059, F1 −0.027. Tidak ada divisi |bias|>0.5 (0/5). Pool per musim dalam
±0.23. **MAE** 2.6–2.8 corner.

**Ladder kalibrasi (pooled, n=12,457):**

| line | p_pred | freq | dev |
|---|---|---|---|
| 6.5 | 0.8254 | 0.8278 | −0.0024 |
| 7.5 | 0.7282 | 0.7271 | +0.0011 |
| 8.5 | 0.6159 | 0.6169 | −0.0011 |
| 9.5 | 0.4983 | 0.4997 | −0.0015 |
| 10.5 | 0.3854 | 0.3821 | +0.0033 |
| 11.5 | 0.2851 | 0.2778 | +0.0073 |

Brier @9.5 = 0.2470; log-loss = 0.6870.

Keputusan: **gate A** (|bias|>0.5 di ≥3/5 divisi searah) tidak terpenuhi;
**gate B** (deviasi >5pp di 9.5) tidak terpenuhi (dev −0.0015).
→ Sesuai instruksi, **model corner TIDAK diubah**; hanya laporan.

Reproduksi: `python experiment_eval_corners.py`

---

## Pekerjaan 3 — Total gol piala per kompetisi (anchor cup rate)

Kumpulkan 272 hasil FT piala dari tipsterarea (scrape halaman tanggal, tanpa
API-Football): **EFL Cup n=171, DFB Pokal n=101**.

Laju gol terukur:

| kompetisi | n | avg_total | avg_home | avg_away |
|---|---|---|---|---|
| EFL Cup | 171 | 3.012 | 1.573 | 1.439 |
| DFB Pokal | 101 | 3.119 | 1.416 | 1.703 |

`cross_lambdas` kini menerima `cup_comp`: anchor total = laju cup penuh saat
n≥100 FT, else blend 50/50 dengan total rating (avg dua divisi). **Rasio λ
home:away dipertahankan** (kedua λ diskalakan faktor sama).

Uji terima (atas 149 EFL + 59 DFB laga terpetakan):

| kriteria | hasil |
|---|---|
| total ≈ cup rate ±0.4 | EFL 3.012 vs 3.012; DFB 3.119 vs 3.119 |
| O/U tidak identik antarlaga | p_gt@2.5: 19 nilai beda (EFL), 18 (DFB) |
| rasio λ |delta| ≤0.01 | max 0.00000 |
| lege byte-identik | `predict_cups` hanya menulis output cup; `predictions_upcoming.csv` tak tersentuh |
| predict_cups jalan penuh | 1 fixture upcoming, skipped 0; Everton-Newcastle total kini 3.012 |

Reproduksi:
```bash
python -c "import predict_cups as pc; pc._cup_goal_rate()"   # laju cup
python -c "import predict_cups; predict_cups.main()"
```

---

## Pekerjaan 4 — Rekomendasi slip odds ±2.0

`slip_recommender.py`: baca `market_compare.csv`, join p_model dari
`predictions_upcoming.csv`/`predictions_cups_upcoming.csv`. Aturan: pasar
1X2/DC/OU/BTS (tanpa corner), satu kaki per laga, 2–4 kaki, p_model≥0.50,
o_1xbet≥1.20, total odds di band 1.85–2.15 (target 2.0); pilih joint probability
tertinggi (tie-break total EV). Tanpa kombinasi in-band → slip terdekat ke 2.0
berlabel `in_band=false`.

Output saat ini (`recommended_slip.csv`):

| date | home | away | market | line | sel | o_1xbet | p_model |
|---|---|---|---|---|---|---|---|
| 2026-10-31 | hull city | ipswich town | DC | | 1X | 1.52 | 0.8288 |
| 2026-10-31 | troyes | le mans | OU | 1.5 | Over | 1.26 | 0.8744 |

**Total 1.915, joint 0.7247, EV 0.3615, in_band=true.**

Terintegrasi ke `run_daily_shadow.py` (langkah 8b, non-fatal) dan
`recommended_slip.csv` masuk arsip harian (`archive/2026-10-29/` kini 7 file).

Reproduksi: `python slip_recommender.py`

---

## Regresi & kendala

- `python test_core.py` → SEMUA TES LULUS.
- `git show HEAD~4..HEAD --name-only`: hanya 4 file sumber berubah
  (`predict_cups.py`, `experiment_eval_corners.py`, `market_orchestration.py`,
  `run_daily_shadow.py`, `slip_recommender.py`). `all_matches_clean.csv`,
  `model_v2.py`, `ta_model.py`, dan file prediksi liga tidak tersentuh.
- Tidak ada pemakaian API-Football baru (satu-satunya sebutan adalah docstring
  lama "TANPA API-Football" di `predict_cups.py:5`).
- Baris piala tidak dicampur ke data latih liga; output cup terpisah.
- File runtime/arsip (`ta/*`, `archive/`, `recommended_slip.csv`) gitignored,
  tidak ikut dikomit.
