# Meta-Stack Warehouse Logits (G-2) — Results

## Ringkasan (Bahasa Indonesia)

**Putusan: GAGAL (FAIL) — tidak ada gerbang yang perlu diperdebatkan, dan
tidak ada yang diadopsi.**

Satu set fitur gudang FotMob yang didaftarkan di muka (3 fitur trailing-10:
selisih kualitas tembakan, selisih peluang besar, selisih xGOT per tembakan
ke gawang) ditambahkan ke stack meta produksi dan diuji walk-forward
bulanan persis seperti produksi. Pada set uji yang identik (laga top-5
musim 2024/25–2025/26, n=3.433, 15 Agustus 2024 – 24 Mei 2026):

- Log loss 1X2 pooled: baseline **0,9710** → varian **0,9711**
  (memburuk +0,0001 — syarat utama gerbang gugur di sini).
- Brier: 0,5776 → 0,5776 (memburuk +0,00009). RPS: 0,1960 → 0,1961
  (memburuk +0,00007).
- Pasar turunan dari probabilitas yang sama (matriks DC terkalibrasi-meta):
  log loss OU 2.5 memburuk +0,00004, BTTS memburuk +0,00001.
- Per musim arahnya berlawanan: 2024/25 membaik −0,0005, 2025/26 memburuk
  +0,0007 — pola khas noise, bukan sinyal. Per divisi juga campur
  (E0 membaik −0,0018; F1 memburuk +0,0021).

Semua selisih berada di skala 0,0001 — jauh di bawah skala efek yang bisa
dipercaya — dan tanda pooled-nya negatif. Ini konsisten dengan kuburan
fitur di `docs/EXPERIMENTS_LOG.md`: stack meta sudah di langit-langit
informasi pasar; bedanya kali ini keluarga fitur gudang juga mati di
level meta, bukan hanya di level DC. Sesuai aturan pra-registrasi, tidak
ada set fitur kedua yang dicoba.

Catatan sanity penting: baseline yang dihitung ulang di pass ini
**persis sama digit-demi-digit** dengan probabilitas meta yang tersimpan
di `records_cache.jsonl` pada set yang sama (LL 0,97102688, Brier
0,57755522, RPS 0,19601209) — mesin walk-forward-nya terverifikasi.
Baseline set-terbatas ini (0,9710) lebih rendah dari standar keluarga
1,0017 karena jendela/set-nya berbeda (hanya top-5, hanya dua musim
terakhir); angka yang berlaku untuk gerbang adalah baseline set-yang-sama.

## Pre-registered feature set (stated before any test result was computed)

Baseline: the 9 logits of `backtest_picks._add_meta_walkforward`
(logit DC probs, logit T3 probs, logit raw implied `1/odds`), monthly
walk-forward refits via `model_features_1x2._fit_params` (defaults),
train = all records with date < the test month, `min_train=1500`.

Variant = baseline + exactly these three extra columns. Per team-match
nets are computed from `data_enrichment/shot_lineup_features.csv`; a
team's value is the mean net over its last 10 warehouse matches
**strictly before** the match date (requires ≥5, else NaN, which
`_fit_params` median-imputes from the training window only); the match
feature is home value − away value:

| Col | Definition (per team-match net) |
|---|---|
| W1 shot-quality diff | `(xg_for/shots_for) − (xg_against/shots_against)` |
| W2 big-chance diff | `big_chances_for − big_chances_against` |
| W3 xGOT/SOT diff | `(xgot_for/sot_for) − (xgot_against/sot_against)` (ratio = 0 when SOT = 0) |

The W columns enter as raw standardised differentials (they can be
negative, so they are not probability logits); `_fit_params` standardises
every column from train only, as for the baseline logits. Lineup
continuity was deliberately excluded — the audit (§1B.2) already
recorded it as a negative result.

## Evaluation window and set

- Test: seasons **2024/25 and 2025/26**, top-5 only (E0, D1, I1, SP1, F1),
  dates **2024-08-15 to 2026-05-24**, **n = 3,433** (of 3,504 top-5
  records in those seasons; 71 excluded because at least one team had
  <5 prior warehouse matches — mostly newly promoted sides early in a
  season — or the warehouse row was absent).
- Training for every test month uses the full prior history (all
  divisions, all seasons before that month), exactly as production;
  warehouse columns are NaN (→ train-median imputation) outside
  top-5 / before 2022/23. Two full warehouse seasons (2022/23, 2023/24)
  precede the test window.
- Derived markets: `matrix_pricer.price(lam_h, lam_a, rho, meta_probs)`
  per model (the Phase-13 production derivation), binary log loss vs
  actual goals.

## Full numbers

### Pooled (n = 3,433)

| Metric | Baseline (9) | Variant (9+3) | Δ (var − base) | Gate |
|---|---|---|---|---|
| 1X2 log loss | 0.9710 | 0.9711 | **+0.0001** | ✗ must improve |
| 1X2 log loss < 1.0017 family standard | 0.9710 | 0.9711 | — | ✓ (both) |
| Brier | 0.5776 | 0.5776 | +0.00009 | ✗ not worse |
| RPS | 0.1960 | 0.1961 | +0.00007 | ✗ not worse |
| OU 2.5 log loss (derived) | 0.6785 | 0.6786 | +0.00004 | ✗ not worse |
| BTTS log loss (derived) | 0.6869 | 0.6869 | +0.00001 | ✗ not worse |
| Accuracy | 0.5357 | 0.5366 | +0.0009 | (info only) |

Precise pooled values: LL 0.971027 → 0.971132; Brier 0.577555 → 0.577644;
RPS 0.196012 → 0.196083; OU LL 0.678525 → 0.678562; BTTS LL 0.686870 →
0.686884.

### Per season

| Season | n | LL base | LL var | ΔLL | Brier Δ | RPS Δ | OU Δ | BTTS Δ |
|---|---|---|---|---|---|---|---|---|
| 2024/25 | 1,711 | 0.9627 | 0.9622 | −0.0005 | −0.00035 | −0.00016 | +0.00023 | −0.00007 |
| 2025/26 | 1,722 | 0.9793 | 0.9800 | +0.0007 | +0.00053 | +0.00030 | −0.00015 | +0.00010 |

### Per division (ΔLL only; full table in `results.json`)

| Div | n | LL base | LL var | ΔLL |
|---|---|---|---|---|
| D1 | 596 | 0.9697 | 0.9693 | −0.0004 |
| E0 | 750 | 0.9944 | 0.9926 | −0.0018 |
| F1 | 602 | 0.9678 | 0.9699 | +0.0021 |
| I1 | 740 | 0.9640 | 0.9637 | −0.0004 |
| SP1 | 745 | 0.9582 | 0.9594 | +0.0012 |

### Sanity vs the recorded family standard

- Same-set recomputed baseline LL **0.9710** vs the family's recorded
  **1.0017**: not comparable head-on — 1.0017 is pooled over the full
  multi-division, multi-season walk-forward, while this set is top-5,
  2024/25–2025/26 only (recent top-5 matches score better). The gate's
  reference is the same-set baseline, per the design.
- The recomputed baseline reproduces the stored `ph_meta` probabilities'
  metrics on the identical set **exactly** (LL/Brier/RPS identical to
  all printed digits), confirming the reimplementation is faithful to
  `_add_meta_walkforward`.
- Production opening-market comparison in the README (Brier 0.5766 /
  RPS 0.1956, broader set) is in the same neighbourhood as this set's
  baseline (0.5776 / 0.1960), as expected.

## Verdict

**FAIL.** Every gate leg except "below the 1.0017 family standard"
fails, all by ~0.0001 — i.e. the warehouse columns add no measurable
information at the meta level on this window; the per-season sign flip
says what little movement exists is noise. No second feature set was
tried (pre-registration discipline). Nothing is adopted; production is
untouched.

## Integration-risk note (had it passed)

Not applicable as an adoption path — but for the record, a pass would
still have carried real integration risk, which is why this experiment
only ever flags, never adopts: (1) live meta fitting
(`make_picks_live._fit_meta`) would need the same trailing-warehouse
computation at prediction time, with FotMob warehouse freshness as a
new hard dependency — a stale warehouse would silently median-impute
the columns and change live probabilities; (2) promoted teams have <5
warehouse matches early in a season, so live coverage would be partial
by design; (3) the records-cache schema and its data stamp would need
to cover the new columns (the Phase-12 bug class: silently training a
9-feature model on all-NaN columns). A ~0.0001-scale effect would never
have justified that risk anyway.

## Artifacts

- `run_experiment.py` — rerunnable (`.venv/bin/python
  experiments/meta_warehouse/run_experiment.py`, ~4 min; monthly refits
  on the full history dominate). Writes `results.json` + `predictions.csv`.
- `results.json` — pooled / per-season / per-division metrics, gate legs.
- `predictions.csv` — per-match baseline and variant probabilities with
  the three warehouse feature values (n = 3,433).
