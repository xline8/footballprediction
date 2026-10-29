# EXPERIMENTS_LOG

Single source of truth for the keep-or-revert loop.
Each experiment: hypothesize → implement → backtest → keep (commit) or revert (log failure).

## Current best baseline (RESET 2026-10-26)

Engine: `backtest_picks.py` (walk-forward, 68,763 test matches, historical B365 opening odds).
Rule: signal = pure model prob, edge = `p − 1/odds` > 0.02, flat 1u stake, 1X2.

| model | yield | log loss | brier | macro-F1 | hit rate | n bets |
|---|---|---|---|---|---|---|
| **DC (baseline)** | **−8.85%** | 1.0311 | 0.6161 | 0.3703 | 0.308 | 46,092 |
| T3 feature | −10.40% | 1.0287 | 0.6171 | 0.3542 | 0.274 | 50,339 |

Goal: yield > 0 while not ruining log loss / Brier. Secondary: lower log loss.

## ⚠️ KOREKSI PENTING (2026-10-26) — de-vigging Shin di-fix

Bug ditemukan di `_fair_probs` cabang shin: bisection terbalik → z≈0.999,
prob fair **jumlah = ~0.52 (bukan 1.0)**, sehingga implied prob terlalu rendah dan
edge terinflasi palsu. Fix: arah bisection dibalik → jumlah prob = 1.0 (tervalidasi
2000 triple odds acak, dan konsisten dgn `mult`).

**Dampak pada semua hasil berbasis shin (Phase 3/4/5):**
- Pocket **Phase 5 S1 (+3.23% flat, 1340 bets) TIDAK bertahan**: dgn shin benar,
  filter top5 favorit 1.2-1.5 edge [0.20,0.22) → **n=0** (edge sebesar itu hampir
  tidak pernah terjadi pada favorit berat). Hasil sebelumnya adalah artefak bug.
- Segmen positif terbaik setelah fix: top5 odds 2.6–3.5 = **+1.88%** (n=512), tapi
  **tidak stabil temporal** (profit terpusat di sampel kecil 2017/2020/2021/2025;
  2023–2026 negatif) → noise, bukan edge.
- Yield global model meta (thr 0.02, shin fixing): **−3.77%** (n=17,093),
  vs DC −9.01% (n=71,015). Model meta jelas lebih baik dari DC; yield global masih
  negatif → odds B365 efisien.
- Kesimpulan: **tidak ada pocket ROI positif yang tervalidasi** setelah koreksi.
  Filter live (`make_picks_live.py`) sengaja dibiarkan menghasilkan **0 pick** agar
  tidak mengirim uang pada edge phantom, sampai strategi dgn edge benar divalidasi
  ulang.

## Progress

| # | hypothesis | config | yield | log loss | brier | verdict |
|---|---|---|---|---|---|---|
| E1 | De-vigging (Shin) | dc/shin/thr .02 | **−7.11%** | 1.0311 | 0.6161 | ✅ KEEP (vs −8.85) |
| E1b | De-vigging (mult) | dc/mult | −8.50…−9.07% | 1.0311 | 0.6161 | ❌ worse than shin |
| E2 | Ensemble blend DC+T3 | blend w .1/.2/.3/.5 + shin | −7.10…−7.17% | 1.020–1.025 | 0.611–0.614 | ❌ no yield gain |
| E3 | Platt recalibration | platt + shin thr .05 | −6.82% | 1.0407 ↑ | 0.6221 ↑ | ❌ ruins logloss/brier |
| E4 | Threshold sweep | shin thr .03/.05/.08/.10/.15/.20 | −6.93…−6.67% | 1.0311 | 0.6161 | ✅ KEEP thr .15 (−6.67%) |
| E4b | Kelly staking | kelly .25 + shin | −8.39% | 1.0311 | 0.6161 | ❌ worse than flat |
| E5 | Draw-specific / T3-at-high-thr | t3 + shin thr .05 | −7.09% | 1.0287 | 0.6171 | ❌ worse than dc |

### Conclusion (after pool exhausted, 7 experiments)

- Best achieved: **DC + Shin de-vigging + edge thr 0.15, flat 1u → yield −6.67%**, log loss 1.0311, Brier 0.6161, hit rate 0.338, 156,871 bets.
- **No configuration reached positive ROI.** The B365 opening odds are efficient; after removing the overround the residual edge is negative. Calibration improves hit-rate but worsens log loss/Brier.
- Recommendation: do **not** switch live bets to any of these. If pursued further, the lever is a genuinely sharper model (more informative features / better calibration *before* edge extraction), not threshold/staking/de-vigging tuning, which are exhausted here.

### Kept (committed)
- `backtest_picks.py` refactor into a configurable engine with `records_cache.jsonl`; default promoted to best config (thin, thr 0.15).

---

## Phase 4 — Core model R&D (target: log loss < 1.020, Brier < 0.600)

Starting baseline (68,763-match walk-forward): DC log loss 1.0311 / Brier 0.6161; T3 feature log loss 1.0287 / Brier 0.6171.

| # | hypothesis | log loss | brier | verdict |
|---|---|---|---|---|
| E1 | Meta-logistic: DC+X3 + market-implied probs | **1.0019** | **0.5989** | ✅ KEEP (both targets hit) |
| E2 | MLP 2-lapis (numpy, 20 fitur) | 1.0126 | 0.6050 | ❌ worse than meta (ll/brier) |
| E3 | Meta + close odds (CLV) | 1.0063 | 0.6001 | ❌ worse than meta (ll/brier) |
| E4 | Per-league (div) meta | 1.0070 | 0.6021 | ❌ worse than meta (ll/brier) |
| E5 | Meta dgn input logit | **1.0017** | **0.5988** | ✅ KEEP (both improve) |
| E6 | Elo decay (K ∝ 1/√play) | 1.0016 | 0.5988 | ❌ noise (≈E5), T3 worsened |

E1 detail: features = p(ph,pd,pa) + p_t3 + (1/o_h,1/o_d,1/o_a) opening odds; multinomial logistic, walk-forward. macro-F1 0.3798, accuracy 0.5031.
E1 ROI (backtest, shin thr 0.15): **yield −5.77%** (vs DC −6.67%), hit rate 36.1%, log loss 1.0045, Brier 0.6004 → also improves the betting leg. Meta promoted to default model.
E5 ROI (logit meta, shin thr 0.15): **yield −5.80%**, hit rate 36.0%, log loss 1.0043, Brier 0.6003 → LL/Brier slightly better, yield flat. Meta (logit) promoted to default.

---

## Phase 5 — GBDT engine + segmented ROI mining

| # | hypothesis | log loss | brier | verdict |
|---|---|---|---|---|
| E1 | LightGBM multiclass (20 fitur, raw+meta) | 1.0032 | 0.5998 | ❌ worse than meta (1.0017/0.5988) |
| E1b | LightGBM (meta-signals only) | 1.0025 | 0.5993 | ❌ worse than meta |
| S1 | Segment sweep: top5 heavy favorite (odds 1.2–1.5) edge ∈ [0.20,0.22) | — | — | ✅ **POSITIVE ROI found** |

S1 detail: **Filtered Value Bet Strategy** — top5 leagues (E0/D1/I1/SP1/F1), odds 1.2–1.5, model edge ∈ [0.20, 0.22):
- flat 1u: **yield +3.23%** on **1340 bets**, hit 74.8% → beats +3.0% target.
- fractional Kelly (0.25): **yield +4.75%** on 145 bets, hit 76.6%.
- Positive across every calendar year 2021–2025 (yearly ~+4–5%, cumulative yield positive throughout) → stable pocket.
- Implemented in `backtest_picks.py --filter [--kelly]`.

⚠️ **DIVALIDASI (2026-10-26)** oleh fix de-vigging shin (lihat KOREKSI di atas):
dgn shin benar, filter ini n=0 → hasil +3.23% adalah artefak bug. Jangan dipakai.

---

## Phase 7 — Deep Feature Science & Market Dynamics

Baseline: meta 9-logit (LL 1.0017, Brier 0.5988), yield backtest shin-corrected thr 0.02 = **−3.77%** (n=17,093). Aturan: KEEP hanya jika LL < 1.0017 **DAN** yield > −3.77%.

| # | hipotesis | fitur | LL | brier | yield (best thr) | n | verdict |
|---|---|---|---|---|---|---|---|
| E1 | Fatigue: rest diff + kepadatan jadwal 14/30 hari | rest_diff, dens14_diff, dens30_diff | 1.0018 ↑ | 0.5989 ↑ | −3.57% (thr .02) | 19,110 | ❌ LL tidak turun |
| E2 | Overperformance xG (gf−xgh, ga−xga rolling 5) | opp_h/a, opc_h/a | 1.0018 ↑ | 0.5989 ↑ | −3.36% (thr .02) | 20,968 | ❌ LL tidak turun |
| E3 | Motivasi: ppm tim + flag musim akhir | ppm_h/a, ppm_diff, late | 1.0017 ≈ (1.001656→1.001704) | 0.5988 ≈ | −3.12% (thr .02); best −1.45% (thr .05) | 2,875 | ❌ LL tidak turun |
| E4 | CLV proxy (pergerakan odds) | — | — | — | — | — | ⛔ tidak dapat diuji: dataset hanya 1 snapshot odds (opening/closing tidak tersedia) |

### Temuan
- **Ketiga hipotesis (E1–E3) gagal gerbang LL** — meta model sudah berada dekat plafon informasi pasar (LL ~1.0017); fitur konteks tidak memperbaiki kalibrasi (LL datar/naik tipis).
- **Namun yield membaik konsisten**: E1 −3.57%, E2 −3.36%, E3 −3.12% (thr .02), semuanya > baseline −3.77%, dan E3 di thr .05 mencapai **−1.45%** (n=2,875) — arah paling menjanjikan. Tidak di-keep karena gerbang LL ketat (dan best-thr dipilih post-hoc, berisiko noise).
- **E4 tidak teruji**: tidak ada snapshot odds kedua, sehingga CLV (movement) tidak bisa dihitung. X koreksi data (closing odds) sebelum hipotesis ini dapat dieksekusi.
- Kesimpulan: tidak ada fitur yang lolos keep per protokol. Yield tetap negatif; tidak ada strategi live yang aktif.

---

## Phase 8 — Dual-Gate Evaluation & Deep Motivation Science

Baseline thr **0.05** (shin, flat): yield **−5.65%** (n=2,158). Gate: LL ≤ 1.00170 DAN yield > −3.77% dgn n ≥ 2,000 (thr pre-fixed .05, tanpa sweep).

| # | hipotesis | fitur | LL | brier | yield (thr .05) | n | verdict |
|---|---|---|---|---|---|---|---|
| 8.1 | Desperation index + interaksi despo×nothing | despo_h/a, nothing_h/a, inter_h/a, rel, eur | 1.0021 ↑ | 0.5991 | −3.27% | 3,834 | ❌ LL degrade |
| 8.2 | GD tie-breaker urgency | u_h/a, gd_h/a, rel | 1.0020 ↑ | 0.5990 | −5.23% | 3,127 | ❌ LL degrade + yield < bar |
| 8.3 | DC × motivasi | dmot_main/h/a, mot_diff | 1.0018 ↑ | 0.5989 | −4.74% | 2,588 | ❌ LL degrade + yield < bar |
| 8.4 | Rest-disadvantage × motivasi | rest_diff, despo, stack_h/a, mot_diff | 1.0021 ↑ | 0.5990 | −3.52% | 3,067 | ❌ LL degrade |

### Temuan & rekomendasi
- **Semua 4 gagal gerbang LL** (1.0018–1.0021 > 1.00170). Fitur motivasi/konteks menambah varians pada estimasi prob rata-rata (LL memburuk) namun **memperbaiki seleksi edge** (yield thr .05 naik dari −5.65% ke −3.27% s.d. −3.52% di 8.1/8.4).
- Pola konsisten sejak Phase 7: meta model sudah pada plafon informasi pasar; fitur konteks tidak menurunkan LL global tapi memindahkan keputusan taruhan ke subset yang lebih menguntungkan. Gerbang LL ketat membuat fitur model hampir mustahil lolos.
- **Rekomendasi jalur berikutnya**: alih-alih menambah fitur ke model prob (mengubah LL), terapkan motivasi sebagai **overlay pasca-model** pada keputusan/stake taruhan (model prob +; LL tidak berubah → gate LL lolos trivial, yield memanen kenaikan 8.1/8.4). Ini bukan "feature stack" per protokol, jadi tidak dieksekusi di sini.
- Tidak ada strategi live aktif; `run_daily_shadow.py` tidak dijalankan karena tidak ada KEEP.

---

## Phase 9 — Decoupled Betting Policy & Contextual Overlay Engine

Arsitektur: **Probability Engine dikunci** (meta model, LL 1.0017 tidak berubah) → edge shin → **Policy Overlay pasca-model** (filter/stake). Evaluasi: yield > −1.50% DAN N ≥ 1,000 DAN yield > 0 di ≥3 dari 2021–2025. Dasar: thr 0.05, flat baseline yield −5.65% (n=2,158).

Framework: `policy_overlay.py` (candidates + desperation index + composite = 0.6·despo + 0.4·fatigue_norm).

| Policy | aturan | hasil terbaik | N | yield | stabil (≥3/5) | verdict |
|---|---|---|---|---|---|---|
| 9.1 | filter despo > θ | θ=0.3 | 169 | +12.7% | 1/5 | ❌ N & stabil |
| 9.2 | filter rest gap ≥ 3 | gap=3 | 44 | +1.8% | 0/5 | ❌ N & stabil |
| 9.3 | filter composite ≥ θ | θ=0.3 | 176 | +11.8% | 1/5 | ❌ N & stabil |
| 9.4 | stake = 0.25·composite | θ=0 | **553** | **+6.7%** | **3/5** | ❌ N<1000 |
| 9.4 floor | stake = 0.25·(f+(1−f)c) | f=0.3 | 2,158 | −4.4% | 2/5 | ❌ yield & stabil |

### Temuan
- **9.4 murni (dynamic contextual Kelly, tanpa floor) adalah satu-satunya konfigurasi dengan yield positif (+6.7%) DAN stabilitas temporal 3/5** — tetapi N=553 < 1,000, jadi gagal gerbang ukuran sampel.
- Menambah floor stake (agar N=2,158) menghapus efeknya: yield kembali negatif (−4.4% s.d. −5.65%), stabil 1–2/5. Artinya keuntungan 9.4 datang justru dari **menghapus** bet berkonteks rendah (stake 0), bukan dari men-stake semuanya.
- Pola: overlay konteks memusatkan taruhan pada subset kecil (200–600 bet) dengan ROI positif-tapi-keras; tidak ada yang lolos N ≥ 1,000 + stabilitas sekaligus.
- **Rekomendasi**: 9.4 adalah lead paling kuat sejauh ini. Untuk lolos N, kumpulkan lebih banyak data (ledger live) atau longgarkan thr edge; opsi lain: ekspansi definisi desperation supaya lebih banyak match ber-score non-nol (risiko dilusi).
- Tidak ada policy yang di-keep → `make_picks_live.py` tidak diubah; flow shadow tetap 0 pick.

---

## Phase 10 — Statistical Significance Test & High-Context Expansion

### Step 1 — Bootstrap significansi Policy 9.4 (`verify_significance.py`, 10,000 resample)
- n bets = 553; ROI weighted = **+6.72%**; bootstrap mean +6.76%; CI95% [−9.48%, +23.44%]; **p-value = 0.2164** (vs H0 ROI≤0).
- **TIDAK signifikan** (p > 0.05) → gate N≥1,000 tidak bisa dilonggarkan atas dasar statistik. CI lebar & pakan nol menunjukkan hasil sangat sensitif thd sedikit bet besar.

### Step 2 — Ekspansi high-context pool (`policy_expand.py`)
- **Proximity kontinental TIDAK tersedia**: div `EC` pada dataset ternyata English National League (Kasta-5 Inggris), bukan Champions/Europa/Conference. Tidak ada jadwal kompetisi klub Eropa → feature cont ≡ 0.
- **Rivalitas (proksi h2h)**: menambah bobot w4 menaikkan N ke 747 tetapi **menghancurkan yield** (+2.8% → +0.3%): proksi h2h tidak prediktif, hanya dilusi.
- **Desperation ekspansi (title/Eropa)**: menaikkan N ke ~562 (dari 553) dgn yield +5.18% (3/5 stable) — mirip 9.4 asli.
- Tidak ada konfigurasi yang mencapai **N≥800 DAN yield>+4.5% DAN stable≥3/5**. Terbaik: base (0.6,0.4) N=562 +5.18% (N kurang); tambah w4 N=747 tapi yield ~0 (gagal).

### Step 3 — Shadow tracking
- Tak lolos karena Step 1 (p=0.216) maupun Step 2 (target N/yield tidak tercapai) → **tidak ada KEEP**, `make_picks_live.py` tidak diubah, live shadow tetap 0 pick.
- Kesimpulan: 9.4 adalah lead terbaik, tapi N=553 terlalu kecil & tidak signifikan. Untuk membuktikan edge perlu lebih banyak data (akumulasi ledger live) atau definisi konteks yang benar-benar prediktif (bukan proksi frekuensi).

---

## Phase 11 — Exogenous Data Enrichment Pipeline (pivot ML → Data Engineering)

Keputusan: dataset historis sudah jenuh oleh meta model (LL 1.0017). Beralih ke pengayaan data eksternal tanpa menyentuh `all_matches_clean.csv`.

### Arsitektur (`data_enrichment/`)
- `utils.py` — normalisasi nama tim (aliases top teams) + fuzzy matching (Levenshtein), parsing float aman, logging.
- `fetch_xg.py` — fetcher understat (xG/xPTS) dgn timeout & fallback ke cache lokal `xg_matches.csv`.
- `fetch_closing_odds.py` — ekstraksi Pinnacle (PSH/PSD/PSA) + Max/Avg dari CSV historis.
- `synthesize_european.py` — heuristic jadwal padat: `midweek_cup_flag` bila tim punya laga lain dalam ±3 hari.
- `enrich_pipeline.py` — left-join → `all_matches_enriched.csv` (mode `--full` / dry-run subset).

### Hasil Dry-Run (EPL 2023/24, 380 match)
| fitur | join | keterangan |
|---|---|---|
| Pinnacle/Max/Avg | 380/380 (100%) | kolom PS sudah ada di sumber |
| xG | 240/380 (63%) | dari cache lokal |
| midweek flag | 120/380 (32%) | konsisten dgn kalibrasi jendela |
| rolling_xg_diff | 380/380 (100%) | leak-free, chronologis |

### Hasil FULL (70,425 match)
Pinnacle/Max/Avg 70,425/70,425; xG 9,074 (12.9%); midweek 21,342 (30.3%); rolling_xg_diff 70,066 (99.5%). Sumber `all_matches_clean.csv` utuh.

### Blocker yang dicatat (→ TODO_AI.md)
1. **understat** tidak dapat ditarik andal (struktur halaman/API berubah, berisiko CAPTCHA) → memakai cache lokal + mock bila gagal.
2. **European fixture asli tidak tersedia**: div `EC` adalah English National League, bukan UCL/UEL/UECL → sintesis heuristic jadwal padat dipakai sbg proxy.
3. **Odds movement murni tidak tersedia** (hanya 1 snapshot odds per match) → Pinnacle/Max/Avg diekstrak sbg proxy CLV lintas-bandar.

---

## Phase 12 — Sharp Book Consensus & Enriched Alpha Integration

Integrasi `all_matches_enriched.csv` (PS Pinnacle, midweek flags, rolling_xg_diff)
ke engine prediksi. Join: 51,420/68,763 rekaman punya PS (83.1%); sisanya
di-imputasi fallback ke B365 (dev=1.0, netral).

### Pathway A — ML injection ke meta model (KEEP ✅)
Fitur meta diperluas 9 → 17: dev_H/D/A (B365/PS), ps_fair (PS de-vigged shin),
midweek_h/a. Walk-forward bulanan, multinomial logistic.

| metrik | baseline meta (9) | +sharp (17) |
|---|---|---|
| log loss | 1.0017 | **1.0013** |
| brier | 0.5988 | **0.5986** |
| macro-F1 | 0.3743 | **0.3768** |
| accuracy | 0.5028 | **0.5035** |

Gate LL < 1.00170: **1.001257 → OK**. Sharp info menurunkan LL (menembus
plafon pasar sebelumnya). **KEEP → dipromosikan sbg baseline meta baru**:
`experiment_meta` diubah ke 17 fitur, `records_cache.jsonl` di-hitung-ulang
(66,379/68,763 meta probs) + kolom `ps`/`mw_h`/`rollxg` dipersistenkan.
Koreksi bug: `augment_records` mula-mula memuat records p/ ps → kolom enriched
semua-NaN → model meta 9 fitur (artefak); di-fix memakai join enriched.

### Pathway B — Policy overlay sharp/soft (REVERT ❌)
Meta dikunci; filter `dev_side > thr` (+/- midweek) pada bet ber-edge (shin).
Gerbang: N ≥ 800 DAN bootstrap p < 0.05 (H0 ROI≤0).

| dev> | mw | N | yield | pos(21-25) |
|---|---|---|---|---|
| 1.00 | 0 | 418 | −4.57% | 2/5 |
| 1.00 | 1 | 89 | −22.47% | 0/5 |
| 1.02 | 0 | 201 | −10.97% | 2/5 |
| 1.02 | 1 | 43 | −35.19% | 0/5 |
| 1.05 | 0 | 65 | −2.63% | 0/5 |
| 1.05 | 1 | 15 | −25.67% | 0/5 |
| 1.08 | 0 | 18 | +32.94% | 0/5 |
| 1.08 | 1 | 5 | −100% | 0/5 |

**Tidak ada konfigurasi mencapai N ≥ 800** (terbaik +32.9% pada n=18 = noise).
Deviasi Pinnacle tanpa midweek justru menyaring ke subset kecil & rugi; dengan
midweek N mengecil drastis. **REVERT → tidak ada overlay baru**, `make_picks_live.py`
tetap 0 pick (tidak ada strategi live aktif).

### Kesimpulan Phase 12
- **Baseline meta baru dipromosikan**: LL 1.0013 (turun), Brier 0.5986. Model
  prob lebih tajam → landasan lebih baik untuk ekstraksi edge ke depan.
- **Tidak ada edge taruhan baru yang tervalidasi** (Pathway B gagal N & signifikanasi).
  Yield global baseline baru menunggu konfirmasi backtest default.

---

## Phase 13 — Derivative Market Expansion & Matrix Pricing

Arsitektur: `matrix_pricer.py` membangun matriks bivariate Poisson DC
(λ_h, λ_a, ρ dari records_cache) lalu **meta-calibrasi** — region Home/Draw/Away
diskala proporsional agar sum 1X2 persis menyamai Meta Model 1.0012. Dari
matriks diturunkan prob Over 2.5 / Under / BTTS. Self-check: marginal 1X2 == meta,
over+under=1, btts pair=1.

### Ketersediaan odds derivatif
- **O/U 2.5**: ada (B365 54,766 match, Pinnacle 48,309) → bisa backtest.
- **BTTS**: TIDAK ada kolom odds historis → data blocker, dicatat di TODO_AI.md;
  logika pricing tetap ada di `matrix_pricer` untuk live shadow.

### Backtest O/U 2.5 (B365, shin de-vigged 2-way, flat 1u, Over+Under)
| thr | N | yield | hit | p_bootstrap |
|---|---|---|---|---|
| 0.02 | 35,412 | −5.66% | 50.2% | 1.0000 |
| 0.05 | 22,193 | −5.98% | 50.0% | 1.0000 |
| 0.08 | 12,479 | −6.19% | 49.8% | 1.0000 |

**TIDAK ada edge**: hit ≈ 50% (base rate O/U) — model tidak menambah sinyal di
atas pasar; yield ≈ −6% ≈ margin B365. p=1.0000 (gagal signifikansi total).
**REVERT aturan taruhan**; **KEEP `matrix_pricer` sbg infrastruktur inti**.
Tidak ada aktivasi live (shadow tetap 0 pick).

---

## Phase 15 — Corners Model Integration & Alpha Validation

Evaluasi `model_corners_v3.py` (Poisson corner, mu berbasis rolling shots,
gamma*/r* di-fit di validasi 19/20–20/21). **Test** walk-forward 2021/22–2025/26,
n=8,906.

### Step 1 — Predictive calibration (murni, tanpa odds)
| metrik | base-rate liga (CB) | shot-based (CS) |
|---|---|---|
| Log loss (NLL total corners) | 2.6169 | **2.6087** |
| Brier Over 9.5 | 0.2483 | **0.2474** |
| MAE total corners | 2.669 | **2.656** |
| RMSE per liga (E0/D1/I1/SP1/F1) | 3.39/3.33/3.38/3.30/3.32 | **3.38/3.32/3.38/3.28/3.32** |

CS mengalahkan CB pada SEMUA metrik & semua liga (konsisten, kecil). Bucket
kalibrasi P(total>9.5): akt/pred 0.46/0.46, 0.55/0.54, 0.60/0.62 → cukup
terkalibrasi. **Model punya sinyal nyata tapi kecil** (LL 2.61 — jauh dari
ideal; model prob tetap berguna utk ranking/risk).

### Step 2 — Backtest ROI
**TIDAK dapat dieksekusi**: odds historis Corners tidak tersedia di
`all_matches_enriched.csv` maupun `clean` (blocker T10). Wiring ke
`backtest_picks.py` + de-vigging + sweep threshold ditunda sampai sumber odds
ada. **Tidak ada aktivasi shadow** (Step 3/4 N/A).

### Status
KEEP `model_corners_v3.py` sbg infrastruktur; blocker T10 dicatat; tanpa alpha
yang tervalidasi.