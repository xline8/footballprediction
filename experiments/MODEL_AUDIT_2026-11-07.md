# Audit Model Non-SOT vs Gudang Data FotMob — 2026-11-07

## Ringkasan (Bahasa Indonesia)

Audit ini mengukur empat model non-SOT (gol, corner, kartu, piala) terhadap gudang
data FotMob yang baru (7.532 respons laga utuh top-5 sejak 2022/23, fitur
tembakan/susunan pemain, pecahan SOT per babak). Tidak ada model produksi yang
diubah; semua angka berasal dari artefak repo dan skrip pengukuran
`experiments/audit_models_2026_11_07.py`.

Temuan utama:

1. **Model gol sudah di langit-langit informasi pasar.** Meta stack produksi
   setara pasar pembuka (RPS 0,1956 vs 0,1955). Diagnosis baru menemukan satu
   mekanisme nyata: probabilitas BTTS terlalu rendah saat laga berjalan dengan
   satu tim tertinggal di babak pertama (selisih −8,5 poin pada irisan tandang
   unggul saat turun minum, n=1.372) — pola "mengejar ketertinggalan" yang sama
   seperti di SOT. Tapi pendahulunya langsung (eksperimen babak SOT V6) gagal
   gerbang, jadi nilainya didiskon besar.
2. **Model corner terverifikasi ulang dari sumber independen.** Hitungan corner
   FotMob cocok persis dengan football-data di 98,4% dari 7.532 laga, dan
   kalibrasi garis 9,5 tidak berubah saat aktual diganti sumbernya (log loss
   0,6869 vs 0,6870). Sisa error corner miring secara terukur terhadap dominasi
   wilayah: laga dengan selisih penguasaan bola dan peluang besar ekstrem
   menghasilkan 0,2–0,3 corner lebih banyak dari prediksi model berbasis
   tembakan — kandidat perbaikan paling konkret di model yang sudah hidup.
3. **Kartu adalah peluang terbesar karena belum ada modelnya sama sekali,**
   sementara labelnya paling lengkap: kartu kuning/merah terisi 100% di file
   bersih untuk lima liga sejak 2017/18. Satu koreksi penting: nama wasit di
   file bersih ternyata HANYA ada untuk Premier League — dan efek wasit pada
   total kartu kuning di sana, setelah dikurangi noise sampling, terukur
   ≈ nol pada jendela 2022/23–2025/26. Desain eksperimen pertama disertakan.
4. **Piala hampir tidak bisa dibantu gudang ini**: gudang hanya berisi laga
   liga. Kualitas kalibrasi piala saat ini praktis belum terukur (baru 1 pick
   piala yang ter-grading di ledger).

Peringatan ukuran efek yang berlaku untuk semua usulan di bawah: semua yang
terukur hari ini berskala kecil (orde 0,001–0,003 log loss), dan beberapa
mekanisme yang terbukti nyata (keadaan turun minum di SOT, susunan pemain asli)
tetap gagal saat diuji jujur. Peringkat di akhir laporan menimbang itu.

---

## Method and honesty rules

- Current-state numbers come only from repo artifacts (`README.md`,
  `docs/EXPERIMENTS_LOG.md`, `ledger/calibration_summary.json`,
  `ledger/ledger_summary.json`, `records_cache.jsonl`,
  `predictions_corners_shots.csv`). Anything not grounded there is marked
  unknown.
- Fresh cuts are computed by `experiments/audit_models_2026_11_07.py`
  (read-only; rerunnable). Walk-forward predictions are the stored ones
  (records cache for goals, the corner model's own backtest artifact) — no
  model was refit for this audit.
- Every slice reports its n. With ~30 slices examined across models, isolated
  ±2pp wiggles are treated as noise; only large, monotone, or
  mechanism-backed patterns are carried into the opportunity lists.

---

## 1. Goals model (1X2 / DC / OU / BTTS)

### A. Current measured state

- **Meta stack (production 1X2): pooled Brier 0.5766 / RPS 0.1956 vs opening
  market 0.5764 / 0.1955** (README.md) — level with the market.
- `docs/EXPERIMENTS_LOG.md` records the meta baseline at log loss 1.0017 and a
  long list of reverted feature families (rest/fatigue, xG overperformance,
  motivation, desperation variants): every one failed to lower log loss. The
  log's own conclusion: the model sits near the market's information ceiling.
- Live recommendation ledger (n=125 graded legs, updated 2026-11-07): overall
  hit 68.8% vs mean_p 73.9% (−5.1pp). By market: OU n=86, −6.9pp; DC n=33,
  +2.4pp; 1X2 n=6, −20pp (sample too small to read). Value-pick ledger: 358
  league picks, ROI −5.79%, mean CLV EV −0.0773, beat-close 53.6%.
- Fresh subset measurement (this audit; stored DC-component probabilities —
  the report probabilities — top-5, 2023/24–2025/26, n=5,256): 1X2 log loss
  0.9829; BTTS log loss 0.6835 with predicted 52.9% vs actual 54.9%; OU 2.5 log
  loss 0.6744 with predicted 52.6% vs actual 53.8%. The DC component mildly
  under-predicts goals/BTTS in recent seasons. (Per-match meta probabilities
  are not stored in the records cache, so the meta stack itself cannot be
  sliced this way without a recompute — a known instrumentation gap.)

### B. Fresh autopsy (warehouse cuts)

1. **BTTS error by half-time state** (mechanism diagnosis; HT state is not
   known pre-match, so this is not a feature — it localises *where* the
   pre-match probability is wrong):

   | HT state | n | BTTS pred | BTTS actual | diff |
   |---|---|---|---|---|
   | Away leading | 1,372 | 53.8% | 62.2% | **−8.5pp** |
   | Home leading | 1,781 | 53.0% | 56.8% | −3.7pp |
   | Level | 2,102 | 52.3% | 48.6% | +3.7pp |

   When a team trails at half-time, both teams score far more often than the
   pre-match model expects — the same chasing mechanism measured for SOT
   (SOT V6: trailing ×1.049 second-half SOT). The pooled −2.0pp BTTS
   under-prediction is the average of these offsetting errors.

2. **1X2 error by lineup continuity** (share of the match's XI that also
   started the team's previous match, averaged over both teams; starter IDs
   from the warehouse; n=5,228 matched):

   | Continuity tercile | mean | DC 1X2 log loss |
   |---|---|---|
   | Low (0.632) | | 0.9575 |
   | Mid (0.772) | n=1,742 each | 0.9965 |
   | High (0.876) | | 0.9962 |

   The naive hypothesis "stable XIs are where the model should shine / churn
   is where it errs" gets **no support** — error is *lowest* in low-continuity
   matches. This is most plausibly confounding (rotation clusters in
   lopsided fixtures involving big squads, which are intrinsically more
   predictable), and the slice variable itself is match-day information.
   Recorded as a negative result: continuity is not an error pocket.

3. **OU 2.5 error by trailing xG differential** (warehouse trailing-10,
   n=5,121): log loss 0.678 / 0.679 / 0.670 across away-edge / balanced /
   home-edge terciles — flat. The DC lambdas already absorb team strength;
   no missed signal here.

### C. Opportunities

- **G-1 — HT-state integration for BTTS (and OU).** *Data:* HT goals already
  in the spine (HTHG/HTAG, complete), plus warehouse halves data for the
  conditional scoring rates. *Experiment:* pre-match distribution over HT
  states from the existing goal model × conditional second-half scoring
  rates estimated walk-forward; tune any blending weight on ≤2022/23, test
  2023/24–2025/26; gate = BTTS log loss improves ≥0.001 pooled with no
  division worsening >0.003 and calibration not worse. *Size class:* the
  slice gap is large (−8.5pp) but the exploitable share is the small part
  predictable pre-match; the direct precedent — SOT V6 halves, same
  mechanism, cleaner data — **failed its gate** (0.6502 vs 0.6488). Expected
  value is therefore discounted hard. *Risks:* double-counting with the DC
  tau correction; HT-state distribution quality caps the gain.
- **G-2 — Warehouse features as extra meta-stack logits.** *Data:*
  shot_lineup_features trailing aggregates (shot quality, big chances,
  lineup continuity — trailing only). *Experiment:* monthly walk-forward
  meta refits exactly as in `backtest_picks._add_meta_walkforward`, adding
  2–4 logits; gate = pooled log loss below the 1.0017 baseline family
  standard and Brier not worse. *Size class:* small; the EXPERIMENTS_LOG
  graveyard says most feature families die here, but they died at the DC
  level — the meta level is where production actually lives and has not
  tried these inputs. *Risks:* features exist only ≥2022/23, so the meta
  test window shrinks; multiple-comparison discipline required (one
  pre-registered feature set, not a fishing pass).
- **Explicitly not opportunities:** naive recalibration of the BTTS/OU
  under-prediction (Platt recalibration was tested in EXPERIMENTS_LOG E3 and
  reverted — it degraded log loss and Brier), and lineup continuity as a
  morning-model feature (negative result above; the JIT-lineup variant also
  failed for SOT in V8).

---

## 2. Corner model

### A. Current measured state

- Backtest artifact `predictions_corners_shots.csv` (the model's own
  walk-forward, test seasons 2021/22–2025/26, n=8,906): shot-based model
  (CS) log loss at line 9.5 = **0.6880** vs league base-rate (CB) 0.7258.
  Calibration (predicted − actual Over rate): line 8.5 −0.38pp, **9.5
  −0.55pp**, 10.5 −0.15pp. Per-season at 9.5: −1.70pp (2021/22), +1.26pp
  (2022/23), −0.79 / −0.81 / −0.76pp (2023/24–2025/26) — a small, persistent
  recent under-prediction of Over.
- Live ledger: **zero graded corner picks** (by_market Corners n=0). The
  model's betting value remains unproven for the same reason as SOT: no
  corner odds are captured anywhere in the system.

### B. Fresh autopsy (warehouse cuts)

1. **Independent-source verification.** FotMob corner counts (features file)
   vs football-data HC/AC on all 7,532 warehouse matches: **exact agreement
   on both teams in 98.4%** (per-division 95.8–99.5%; worst E0 95.8%), MAE on
   the match total 0.02 corners. Re-scoring the backtest's 9.5-line
   probabilities against FotMob actuals on the overlap (n=7,081): log loss
   0.6870 vs 0.6869 against football-data actuals; actual Over rate 49.29%
   vs 49.34%. **The model's calibration verdict is source-independent** —
   football-data corner labels are not the bottleneck.
2. **Residuals by trailing territorial dominance** (test seasons
   2023/24–2025/26; residual = actual − predicted total corners):
   - Trailing possession differential: extreme buckets −0.183 (n=1,748,
     away-dominant) and **+0.204** (n=1,758, home-dominant); middle buckets
     noisy (−0.044…+0.178, n≈520–580 each).
   - Trailing big-chance differential: top bucket **+0.323** (n=962),
     bottom bucket −0.009 (n=935), middle ≈ −0.13…−0.05.
   Matches where one side territorially dominates (possession, big chances —
   beyond raw shot counts, which the model already uses) systematically
   produce ~0.2–0.3 more corners than predicted. The two cuts agree in
   direction; the mid-range is noise, so treat this as an extremes effect,
   not a smooth law. Multiple-comparison caution applies (~10 buckets).
3. **Half-split availability.** Store period stats: FirstHalf corners
   present in 19/60 sampled matches for 2022/23 (32%) and **60/60 for every
   season from 2023/24 on**. First-half share of total corners: mean 0.472,
   sd 0.174 (n=400, 2024/25–2025/26) — a half-corner target is well-defined
   and labelled for three full seasons.

### C. Opportunities

- **C-1 — Territorial-dominance multiplier on the corner mean.**
  *Data:* trailing possession and big-chance differentials from
  shot_lineup_features. *Experiment:* extend `model_corners_v3.run_wf` with
  a gamma-style multiplier exp(β·z) on mu_cs; warehouse features only exist
  ≥2022/23, so the honest restricted design is: fit β on 2022/23+2023/24,
  test 2024/25+2025/26 (n≈3,503); gate = pooled LL@9.5 improves ≥0.001, no
  test season worsens, calibration diff does not grow. *Size class:* mean
  residual tilt ~0.2–0.3 corners at the extremes → expected LL gain at the
  small end of the usual scale. *Risks:* possession/big chances correlate
  with shots (the model's existing input) — incremental value is exactly
  what the experiment must prove; shorter test window than the model's
  convention.
- **C-2 — Half-corner model (1H total corners).** *Data:* store period
  stats (full coverage 2023/24+, partial 2022/23). *Experiment:* clone the
  corner recipe on 1H totals (team 1H corner for/against ratings from the
  same period stats, NB distribution); tune on 2023/24, test
  2024/25–2025/26; gate = beats 1H league base-rate and a naive
  0.472×FT-model benchmark on LL at the central line, calibration ≤1pp.
  *Size class:* new market, accuracy unknown; the FT model's recipe
  transferred cleanly to SOT, which is encouraging but not evidence.
  *Risks:* no known odds source for 1H corners (value unprovable today);
  2022/23 labels unusable (32% coverage).
- **C-3 — FotMob as second actuals source for grading.** Not an accuracy
  item: with 98.4% exact agreement, FotMob actuals can grade corner
  predictions where football-data has no coverage (notably cup matches, if
  cup responses are ever pulled — see §4). Cheap data plumbing; listed for
  completeness, ranked last among corner items.

---

## 3. Cards — no production model (feasibility audit + first-experiment design)

### A. What exists today

No cards model, no cards predictions, no cards grading. The user flagged
cards as the next market candidate on 2026-11-07 (after SOT) precisely
because the labels were believed to be in-house. This section verifies that
belief field by field.

### B. Data verification (measured)

**Clean file (the would-be label source):**
- HY/AY/HR/AR (and HF/AF) are **100% populated for the top-5 in every season
  2017/18–2026/27** (16,560 spine matches with FT SOT; cards coverage
  measured per season at 99.9–100.0%). Full training history exists — unlike
  warehouse features, a cards model is not limited to ≥2022/23.
- **Referee names are populated for only ~21% of top-5 rows — that is
  exactly the E0 share (380 of 1,826 per season).** The standing assumption
  "referee is in the clean file" is true for the Premier League only; the
  other four divisions have no referee column data in football-data files.

**Warehouse (FotMob store):**
- Discipline per match is extracted in shot_lineup_features (yellow/red/
  fouls per team). Cross-check vs the clean file on 7,531 matched matches:
  **exact agreement — yellows 89.7%, reds 99.2%, fouls 95.9%.** The yellow
  gap is definitional (second-yellow/red bookkeeping differs by source).
  Conclusion: keep the clean file as the single label source; FotMob is a
  valid cross-check, not a replacement.
- Period stats carry a discipline group and FirstHalf yellow cards wherever
  periods exist (2023/24 onward: 100% of sampled; 2022/23: 32%). First-half
  share of total yellows: mean **0.327** (sd 0.281, n=390) — cards are
  heavily second-half-loaded, which any halves variant must respect.
- A `referee` field string is present in header/matchFacts of **300/300
  sampled store JSONs** across divisions — referee identity for all top-5
  leagues is very likely extractable from the warehouse (field-level
  extraction not yet built or verified). This is the only known route to
  non-E0 referee data.

**Base rates and dispersion (top-5, 2022/23–2025/26, n=7,081):**
- Total yellows: mean **4.077**, variance/mean **1.133** (mild
  overdispersion — an NB with r ≈ 31, the same shape family as SOT's
  1.107). Total cards (Y+R): mean 4.271.
- By division (mean yellows): SP1 **4.67**, I1 4.09, D1 3.99, E0 3.89,
  F1 **3.67** — a full card per match separates the most and least
  card-heavy leagues; league base rates alone will carry real signal.

**Referee effect — measured, and it is ≈ 0 at this aggregation:**
E0 only, 19 referees with ≥40 matches in 2022/23–2025/26: between-referee
variance of mean total yellows = 0.057, vs ≈0.059 expected from sampling
noise alone → excess variance ≈ **0.000**. Whatever referee differences
exist in this window are smaller than the noise floor of a 40–90 match
sample at the match-total level. (This does not rule out team×referee or
per-team effects; it rules out leading the design with a referee main
effect.)

### C. First-experiment design (not built)

Clone the corner/SOT recipe, which has now transferred successfully once:
- **Target:** total yellows per match, O/U lines 3.5 / 4.5 / 5.5 (central
  line 4.5); secondary target Y+R if the primary passes.
- **Model:** venue-split team ratings for cards-for and cards-against
  (trailing, exponential decay — tune half-life in {180, 270, 365} on the
  tuning window), division base rates, Negative Binomial with r estimated
  from tuning residuals (prior expectation ≈ 31). No referee term in v1
  (per §B); E0-only referee add-on is a pre-registered v2 question, and a
  warehouse referee extraction is a data prerequisite for extending it.
- **Split:** tune on ≤2022/23 (labels complete back to 2017/18 — use the
  same walk-forward discipline as the corner model), test on
  2023/24–2025/26 (n=5,255).
- **Gate (pre-registered):** pooled log loss at line 4.5 beats (a) the
  division base-rate baseline and (b) a naive trailing-10 team-average
  baseline; pooled calibration |diff| ≤ 1pp; no division worse than the
  base-rate baseline by >0.003 LL. Fail = stop, report, no production file.
- **Risks:** no cards odds are captured anywhere in the system, so betting
  value is unprovable offline (identical blocker to SOT/corners — accuracy
  first, market later); label definition must stay single-source (clean
  file) to avoid the 10% yellow definitional drift; SP1's high base rate
  makes it the division most likely to embarrass a pooled fit — the gate's
  per-division leg exists for exactly this (cf. Serie A in the SOT
  program).

---

## 4. Cups (EFL Cup + DFB Pokal) — brief

### A. Current measured state

- Design (from `predict_cups.py`): only fixtures where **both** teams map to
  league data (E0–E3, D1–D2) are predicted; goals come from per-division DC
  fits with cross-division lambdas anchored to a blend of division scoring
  rates and the measured cup scoring rate (ramp n/100 from ta/results);
  corners come from rolling 5-match league shots, skipped when a team has
  <3 such matches. The module itself declares cross-division calibration
  unmodelled.
- Graded evidence is effectively **absent**: the value-pick ledger's cup
  buckets contain EFL Cup n=1 graded pick (OU, +0.22u, no CLV coverage) and
  DFB Pokal n=0. Cup calibration quality is unknown — not bad, not good:
  unmeasured. `predictions_cups_upcoming.csv` currently holds no fixtures.

### B/C. What the warehouse can and cannot do

- **Cannot (structural):** the store contains league matches only — no cup
  fixtures, no cup lineups, no cup actuals. The defining cup phenomenon,
  **rotation**, is invisible in league data: a Premier League side's cup XI
  routinely differs from its league XI by half the team, and the warehouse
  holds only the league XIs. Cup corner actuals exist nowhere in-house
  (cup corners are predicted but, by design, never graded).
- **Can (marginal):** richer pre-match form features for cup participants
  from their league matches (trailing xG / shot quality / lineup data
  ≥2022/23) — the same feature families that produced no adoptable gain for
  goals or SOT today, so expected value is low.
- **One concrete data opportunity (completeness, not accuracy):** FotMob
  carries both cup competitions; a targeted pull of cup responses (same
  machinery as `pull_fotmob_full.py`, fixtures resolved via TipsterArea's
  cup fixture list) would create cup actuals — goals, corners, cards —
  making cup predictions gradeable for the first time. Only after a graded
  sample exists does any cup modelling question become measurable. No
  experiment is designed here because there is currently nothing to judge
  one against.

---

## 5. Ranked shortlist (cross-model)

Ranking = signal strength × data readiness ÷ cost, discounted by today's
lessons (real mechanisms repeatedly failed gates; adoptable gains were
~0.001–0.003 log-loss scale).

| # | Opportunity | Signal evidence | Data readiness | Cost | Expected class |
|---|---|---|---|---|---|
| 1 | **Cards first model** (§3C design) | Division base-rate spread 3.67–4.67 yellows; recipe transferred twice (corners, SOT); NB shape fits (var/mean 1.133) | Labels 100% since 2017/18, all top-5 | One experiment build (clone) | New market; accuracy testable offline end-to-end |
| 2 | **Corner territorial multiplier** (C-1) | Residual tilt +0.20/+0.32 corners at dominance extremes, two agreeing cuts, n≈1,000–1,800 per extreme bucket | Features ready ≥2022/23 | Small extension of run_wf; restricted test window (fit 22/23–23/24, test 24/25–25/26) | Small LL gain if real (~0.001 scale) |
| 3 | **Goals BTTS via HT-state integration** (G-1) | Largest single slice gap found (−8.5pp, n=1,372) | HT goals complete in spine | Medium (state-distribution machinery) | **Discounted**: direct SOT precedent (V6) failed its gate with the same mechanism |
| 4 | **Half-corner model** (C-2) | FT recipe's transferability; 1H share 0.472±0.174 | Period labels full 2023/24+ | One clone build; shorter history | New market; no odds source known |
| 5 | **Meta-stack warehouse logits** (G-2) | None direct — untested input family at the meta level | Features ≥2022/23 only | Small (existing stack machinery) | Low: EXPERIMENTS_LOG feature graveyard + market ceiling |
| 6 | **Cup actuals pull** (§4) | None (no graded cup sample exists to improve against) | FotMob carries both cups; pull machinery exists | One data pull + grading wiring | Completeness only — enables future measurement, no accuracy claim |

**Rejected with evidence (do not retry as designed):** lineup continuity as
a goals-model feature (error is lowest where continuity is lowest — §1B.2);
naive recalibration of BTTS/OU (reverted in EXPERIMENTS_LOG E3 for degrading
log loss/Brier); referee-led cards adjustment (excess between-referee
variance ≈ 0.000 in the E0 window — §3B); per-division blanket corrections
and slice patches generally (failed repeatedly in the SOT program — V2 +4,
V4; structural/machine changes were the only adoptable gains).

*Audit scripts: `experiments/audit_models_2026_11_07.py`. No production
model or pipeline file was modified.*
