# Model SOT v9 — Produk Pecahan Babak (1H / 2H / Total)

## Ringkasan (Bahasa Indonesia)

Pertanyaan: v6 membangun mesin rating per babak tetapi hanya dinilai sebagai peningkat total full-time — dan gagal di gerbang itu. Di sini pecahan babak dinilai sebagai PRODUK tersendiri: total full-time tetap ekspektasi produksi v5, yang baru adalah PECAHANNYA — porsi SOT tiap tim yang dimodelkan jatuh di babak 1 vs babak 2 (rating per babak + pengali keadaan turun minum beku dari v6), dinilai melawan dua baseline pecahan pada total v5 yang sama.

Jawaban: **TIDAK LOLOS gerbang pra-registrasi**. Pada 5,254 laga uji lima liga top (2023/24–2025/26; 1 laga tanpa label babak dilewati): log loss pooled babak 1 produk 0.6070 vs baseline (a) 0.6067; babak 2 produk 0.6154 vs baseline (a) 0.6142. Kalibrasi babak 1: 0.77pp vs 0.92pp; babak 2: 0.73pp vs 0.89pp. Produk TIDAK dibangun; produksi tetap v5 total saja.

## Frozen quantities (tuning era only, <=2022/23)

- League 1H share S (baseline a), from 6,888 halves-labelled top-5 matches in 2019/20–2022/23: **0.4563**
- NB sizes by method of moments on walk-forward warm-up residuals (same 6,888 matches): r_1H = **86.39**, r_2H = **1000.00** (FT reference r = 79.94). The r_2H figure is the estimator's cap: the raw 2H moment denominator was slightly negative (Σ(y−mu)²/n = 4.859 vs Σmu/n = 4.877), i.e. warm-up 2H totals were essentially Poisson-dispersed around the product means, so r_2H → ∞ and was capped at 1000 (≈ Poisson). All three variants share the same per-half r, so the split comparison is unaffected by the cap.
- HT-state multipliers (frozen in v6): lead 0.964, level 0.978, trail 1.049. Ridge lambda = 100, BB prior = 200 (v5 warm-up re-derived, asserted).
- FT continuity check on the scored set: v5 ensemble line-9.5 log loss 0.6488 (v6 reported 0.6488 on all top-5 test matches; the scored set here drops the 1 unlabelled match).

## Headline — per half, pooled over the half's lines

| Variant | 1H log loss | 1H calib (pp) | 1H MAE | 2H log loss | 2H calib (pp) | 2H MAE |
|---|---|---|---|---|---|---|
| PRODUCT (v5 total x modelled share) | 0.6070 | 0.77 | 1.58 | 0.6154 | 0.73 | 1.77 |
| baseline (a) constant league share | 0.6067 | 0.92 | 1.58 | 0.6142 | 0.89 | 1.77 |
| baseline (b) naive trailing team share | 0.6252 | 0.89 | 1.63 | 0.6330 | 0.42 | 1.82 |

## Per line — 1H (lines 3.5, 4.5, 5.5)

| Variant | Line | LogLoss | Pred Over% | Actual Over% |
|---|---|---|---|---|
| PRODUCT (v5 total x modelled share) | 3.5 | 0.6709 | 56.3 | 56.4 |
| PRODUCT (v5 total x modelled share) | 4.5 | 0.6454 | 37.5 | 36.6 |
| PRODUCT (v5 total x modelled share) | 5.5 | 0.5046 | 22.4 | 21.1 |
| baseline (a) constant league share | 3.5 | 0.6710 | 56.6 | 56.4 |
| baseline (a) constant league share | 4.5 | 0.6450 | 37.7 | 36.6 |
| baseline (a) constant league share | 5.5 | 0.5040 | 22.5 | 21.1 |
| baseline (b) naive trailing team share | 3.5 | 0.6891 | 55.1 | 56.4 |
| baseline (b) naive trailing team share | 4.5 | 0.6645 | 36.9 | 36.6 |
| baseline (b) naive trailing team share | 5.5 | 0.5219 | 22.3 | 21.1 |

## Per line — 2H (lines 4.5, 5.5, 6.5)

| Variant | Line | LogLoss | Pred Over% | Actual Over% |
|---|---|---|---|---|
| PRODUCT (v5 total x modelled share) | 4.5 | 0.6848 | 52.4 | 53.5 |
| PRODUCT (v5 total x modelled share) | 5.5 | 0.6445 | 35.2 | 35.9 |
| PRODUCT (v5 total x modelled share) | 6.5 | 0.5170 | 21.5 | 21.9 |
| baseline (a) constant league share | 4.5 | 0.6834 | 52.2 | 53.5 |
| baseline (a) constant league share | 5.5 | 0.6434 | 35.1 | 35.9 |
| baseline (a) constant league share | 6.5 | 0.5157 | 21.3 | 21.9 |
| baseline (b) naive trailing team share | 4.5 | 0.7019 | 52.7 | 53.5 |
| baseline (b) naive trailing team share | 5.5 | 0.6637 | 35.9 | 35.9 |
| baseline (b) naive trailing team share | 6.5 | 0.5336 | 22.3 | 21.9 |

## By division — pooled log loss per half

| Div | 1H product | 1H base (a) | Δ1H | 2H product | 2H base (a) | Δ2H |
|---|---|---|---|---|---|---|
| E0 | 0.6225 | 0.6234 | -0.0010 | 0.6224 | 0.6206 | +0.0018 |
| D1 | 0.6327 | 0.6318 | +0.0009 | 0.6350 | 0.6350 | +0.0000 |
| I1 | 0.5848 | 0.5834 | +0.0014 | 0.5847 | 0.5838 | +0.0009 |
| SP1 | 0.5837 | 0.5833 | +0.0004 | 0.6085 | 0.6083 | +0.0002 |
| F1 | 0.6185 | 0.6185 | -0.0000 | 0.6340 | 0.6303 | +0.0037 |

## Gate verdict (pre-registered)

- Product beats baseline (a) pooled log loss on BOTH halves: **NO** (1H 0.6070 vs 0.6067; 2H 0.6154 vs 0.6142).
- Product not worse-calibrated than (a) by >0.5pp on either half: **YES** (1H 0.77 vs 0.92pp; 2H 0.73 vs 0.89pp).
- **Verdict: FAIL — do not build; production stays v5 total only.**

## Method notes and caveats

- The v5 total used here is the model MEMBER production writes as its expectation (0.5 * regression + 0.5 * BB shots-implied per team); the naive ensemble member enters only the FT continuity check, exactly as in production probabilities.
- The split is normalised per team, so product 1H + 2H expectations sum to the v5 total by construction; the halves are graded against halves actuals only — no claim is made here about improving the FT total (v6 already answered that: it does not).
- Halves are intrinsically noisier than full-time totals (roughly half the counts, plus HT-state variance); per-half log losses are not comparable to FT line log losses.
- Reading of the failure: the modelled share clearly beats the naive trailing team share (baseline b) on log loss in both halves, so the machinery does extract real split signal — but the constant league share (S = 0.4563) is a very strong prior, and the product's per-match share variation adds slightly more variance than signal on log loss (worst cell: F1 2H, +0.0037), even though its average calibration is better than the constant's on both halves. Under the pre-registered bar (must win log loss on BOTH halves), that is a fail; the bar was not moved after seeing the numbers.
- Test-season halves-label coverage: all scored matches come from sot_halves_combined.csv; 1 top-5 test match(es) had no label and were skipped for half scoring.
- Script runtime: 47s. No production code touched by this script; no odds anywhere.
