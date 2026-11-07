# Shots-on-Target (SOT) Model — v7: FotMob Shot/Lineup Features on v5

## Ringkasan (Bahasa Indonesia)

Putaran ini menguji empat grup fitur baru dari data FotMob di atas model produksi v5. Hasilnya: **tidak ada grup yang lolos gerbang** — G1 memperburuk (ΔLL +0.0019); G2 memperburuk (ΔLL +0.0005); G3 membantu sedikit tapi gagal di kaki gerbang lain (ΔLL -0.0012); G4 membantu sedikit tapi gagal di kaki gerbang lain (ΔLL -0.0012). Kombinasi grup yang selamat dari penyetelan (G1, G2, G3, G4) juga tidak lolos. **Produksi tetap v5, tidak diubah.** Angka patokan pada set yang sama: v5 log loss 0.6488, kalibrasi 0.0pp (n=5,255). Satu catatan data penting: uji G2 (dan satu komponen G1) memakai flag isFromInsideBox dari FotMob yang cakupannya tidak merata antar-musim (hampir kosong di 2022/23, penuh baru dari 2024/25), jadi ide lokasi tembakannya belum teruji bersih — tindak lanjut yang wajar adalah membagi lokasi dari koordinat x/y tembakan, bukan dari flag itu.

## Setup

Script: `run_sot_v7.py` (re-runnable; reuses `run_sot_v2.py` data loading/ratings and `run_sot_v5.py`'s regression store / slim components unchanged). Reference: production v5 = slim + R + NB + BB with ridge lam = 100 and BB prior P = 200 (production's frozen constants) and NB r = 79.94 estimated in-pass by v5's own warm-up procedure (production froze 79.94).

- Features file: 7,532 matches (top-5, seasons >= 2022/23); joined 7,532 of the model's match rows.
- Extra store extraction (location splits, shooter shares, starter sets) cross-checked against the flat CSV: inside-box counts agree on 15,062/15,062 team-matches, SOT totals on 15,062/15,062.
- Same evaluation set: 5,255 top-5 test matches present in the features file (of 5,255 top-5 test matches; 0 missing from the file). Feature layer unavailable (fallback to plain v5, counted) for 135 of them.
- Tuning set: 1,580 recorded 2022/23 matches (of 1826 top-5 features matches that season; 246 without enough trailing history). Minimum trailing history: 5 matches; window: last 10.

## Sanity anchor — v5 on the FULL standard test set

v5 recomputed over all 21,461 test matches (2023/24–2025/26, all divisions): pooled line-9.5 log loss **0.6304** (RESULTS_V5.md: 0.6304), Brier 0.2198, calib err 0.2pp → **MATCH — run valid**.

## Frozen choices (2022/23 only)

- v5 tuning-set log loss (line 9.5, recorded matches): 0.6419.
- G1 coefficient beta (grid over the tuning set): b=0: 0.6419, b=0.01: 0.6418, b=-0.01: 0.6420, b=0.02: 0.6417, b=-0.02: 0.6421, b=0.04: 0.6417, b=-0.04: 0.6424, b=0.07: 0.6418, b=-0.07: 0.6430, b=0.1: 0.6421, b=-0.1: 0.6438, b=0.15: 0.6429, b=-0.15: 0.6455, b=0.2: 0.6443, b=-0.2: 0.6477, b=0.3: 0.6483, b=-0.3: 0.6535 → chosen **beta = 0.04** (survivor)
- G3 coefficient beta (grid over the tuning set): b=0: 0.6419, b=0.01: 0.6421, b=-0.01: 0.6417, b=0.02: 0.6424, b=-0.02: 0.6415, b=0.04: 0.6430, b=-0.04: 0.6412, b=0.07: 0.6441, b=-0.07: 0.6411, b=0.1: 0.6456, b=-0.1: 0.6412, b=0.15: 0.6485, b=-0.15: 0.6421, b=0.2: 0.6520, b=-0.2: 0.6436, b=0.3: 0.6606, b=-0.3: 0.6486 → chosen **beta = -0.07** (survivor)
- G4 coefficient beta (grid over the tuning set): b=0: 0.6419, b=0.01: 0.6418, b=-0.01: 0.6420, b=0.02: 0.6417, b=-0.02: 0.6421, b=0.04: 0.6417, b=-0.04: 0.6425, b=0.07: 0.6419, b=-0.07: 0.6432, b=0.1: 0.6424, b=-0.1: 0.6441, b=0.15: 0.6437, b=-0.15: 0.6460, b=0.2: 0.6458, b=-0.2: 0.6484, b=0.3: 0.6519, b=-0.3: 0.6542 → chosen **beta = 0.04** (survivor)
- G2 blend weight w: w=0: 0.6419, w=0.25: 0.6414, w=0.5: 0.6410, w=0.75: 0.6407, w=1: 0.6406 → chosen **w = 1** (survivor)
- Standardisation constants (mu/sd of trailing components, pooled over both teams at recorded 2022/23 matches): xg_shot 0.109/0.020, xgot_shot 0.104/0.027, in_share 0.052/0.089, deep_share 0.881/0.047, blk_share 0.258/0.049, top3_shot 0.641/0.054, top3_sot 0.876/0.068, cont 0.765/0.093, big_pm 2.025/0.847, poss 50.029/6.824, opp_big_ag_pm 2.021/0.775.

## Headline — pooled line 9.5, same evaluation set

| Variant | n | LogLoss | Brier | Calib err (pp) | ΔLL vs v5 | Δcalib (pp) | Worst div ΔLL | Gate |
|---|---|---|---|---|---|---|---|---|
| v5 (production reference) | 5,255 | 0.6488 | 0.2285 | 0.0 | — | — | — | reference |
| v5 + G1 shot quality | 5,255 | 0.6507 | 0.2294 | 2.5 | +0.0019 | +2.5 | +0.0049 | no |
| v5 + G2 location-aware ratio | 5,255 | 0.6493 | 0.2287 | 0.4 | +0.0005 | +0.4 | +0.0014 | no |
| v5 + G3 concentration & continuity | 5,255 | 0.6476 | 0.2279 | 0.6 | -0.0012 | +0.6 | -0.0003 | no |
| v5 + G4 match stats | 5,255 | 0.6476 | 0.2279 | 0.7 | -0.0012 | +0.7 | -0.0003 | no |
| v5 + surviving groups combined | 5,255 | 0.6505 | 0.2294 | 3.4 | +0.0017 | +3.4 | +0.0058 | no |

MAE (same set): v5 2.41, combined 2.50.

## v5 vs combined at every line (same set)

| Variant | 7.5 | 8.5 | 9.5 | 10.5 |
|---|---|---|---|---|
| v5 (production reference) | 0.6311 | 0.6710 | 0.6488 | 0.5694 |
| v5 + surviving groups combined | 0.6318 | 0.6716 | 0.6505 | 0.5723 |

## By division (top-5) — line 9.5 log loss, same set

| Div | n | v5 (production reference) | v5 + G1 shot quality | v5 + G2 location-aware ratio | v5 + G3 concentration & continuity | v5 + G4 match stats | v5 + surviving groups combined |
|---|---|---|---|---|---|---|---|
| E0 | 1,140 | 0.6648 | 0.6697 | 0.6650 | 0.6640 | 0.6644 | 0.6706 |
| D1 | 917 | 0.6780 | 0.6787 | 0.6794 | 0.6748 | 0.6761 | 0.6770 |
| I1 | 1,140 | 0.6098 | 0.6133 | 0.6095 | 0.6084 | 0.6089 | 0.6106 |
| SP1 | 1,140 | 0.6314 | 0.6307 | 0.6325 | 0.6311 | 0.6297 | 0.6315 |
| F1 | 918 | 0.6697 | 0.6704 | 0.6702 | 0.6690 | 0.6686 | 0.6724 |

## Combined by season — line 9.5 (v5 alongside)

| Season | n | Combined LogLoss | Combined calib (pp) | v5 LogLoss |
|---|---|---|---|---|
| 2023/24 | 1,752 | 0.6512 | 0.1 | 0.6545 |
| 2024/25 | 1,751 | 0.6513 | 5.2 | 0.6470 |
| 2025/26 | 1,752 | 0.6492 | 5.1 | 0.6449 |

## Gate verdict

- v5 + G1 shot quality: ΔLL +0.0019 (must be < 0: NO); calib 2.5pp, Δcalib +2.5pp (must be <= 0: NO); worst top-5 division ΔLL +0.0049 (limit +0.003: NO) → **not adoptable**.
- v5 + G2 location-aware ratio: ΔLL +0.0005 (must be < 0: NO); calib 0.4pp, Δcalib +0.4pp (must be <= 0: NO); worst top-5 division ΔLL +0.0014 (limit +0.003: ok) → **not adoptable**.
- v5 + G3 concentration & continuity: ΔLL -0.0012 (must be < 0: ok); calib 0.6pp, Δcalib +0.6pp (must be <= 0: NO); worst top-5 division ΔLL -0.0003 (limit +0.003: ok) → **not adoptable**.
- v5 + G4 match stats: ΔLL -0.0012 (must be < 0: ok); calib 0.7pp, Δcalib +0.7pp (must be <= 0: NO); worst top-5 division ΔLL -0.0003 (limit +0.003: ok) → **not adoptable**.
- v5 + surviving groups combined: ΔLL +0.0017 (must be < 0: NO); calib 3.4pp, Δcalib +3.4pp (must be <= 0: NO); worst top-5 division ΔLL +0.0058 (limit +0.003: NO) → **not adoptable**.
- **No variant is adopt-worthy — production stays on v5 unchanged.**

## Data caveat — isFromInsideBox feed coverage

The inside-box flag behind the CSV's `inside_box` column (and therefore behind G1's inside-share component and ALL of G2's location split) is not populated uniformly over time. Share of shots flagged inside the box, by season: 2022/23: 5.6%, 2023/24: 34.6%, 2024/25: 66.7%, 2025/26: 66.0%, 2026/27: 65.0%. A real inside-box share is ~65% (the level seen once the flag is fully populated, 2024/25 on); in 2022/23 — the tuning season — the flag is essentially absent, and 2023/24 is transitional. Consequences: (i) G2's verdict is CONFOUNDED — the location idea was tuned and partly tested on a missingness pattern, not on football; a coordinate-based split (shot x/y are populated for nearly every shot) is the clean follow-up test, as its own pre-registered round. (ii) G1 carries the same contamination in one of its five components; its other four (xG/shot, xGOT/shot, deep share, blocked share) do not use the flag. (iii) G3 and G4 do not use the flag at all — their reads are clean.

## Method notes and caveats

- Integration is a machine change, not a slice patch: G1/G3/G4 multiply each team's v5 blended expectation by exp(beta * z) with ONE tuned coefficient per group (z = mean of standardised trailing components); G2 rebuilds the ratio stage with location-specific on-target ratios and blends it with the BB ratio at the tuned weight. The naive ensemble member and the NB size are never touched.
- Trailing pools are venue-first (last 10 at the same venue when >= 5 exist, else last 10 overall when >= 5 exist). Feature state updates in the same sequential match order as the ratings machinery, including its within-day ordering — parity with the house walk-forward discipline, documented rather than hidden.
- G2/G3 raw material (location splits, shooter shares, starter identities) is extracted from the FotMob store JSONs because the flat features CSV carries only starter counts; counting rules mirror the CSV extractor exactly (QC above). The cache is `v7_extra_features.csv` next to this script.
- G1 uses the attack side only (a team's own shot quality); the opponent's conceded quality is not modelled — the ratings/defence terms already carry opponent strength. G4 does use the opponent's trailing big-chances-conceded, which is a matchup property, not a slice correction.
- Post-match fields in the features file (team_rating, same-match unavailable counts, the match's own stats) are never used; lineup continuity uses only starter sets of strictly earlier matches.
- Fallback matches (feature layer unavailable) are scored as plain v5 for every variant, so all variants share one n and the comparison is apples-to-apples; the dilution is symmetric.
- No odds anywhere: predictive accuracy/calibration only, not betting value (no SOT odds in our data).
- Script runtime (this run, incl. data load and store extraction): 63s.
