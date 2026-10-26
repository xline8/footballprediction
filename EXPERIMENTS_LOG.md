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
