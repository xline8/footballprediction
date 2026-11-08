# Phase 4 — Model Design: NO-OBOSLigaen Candidates

Rules of construction inherited from `league/J1/analysis/MODEL_DESIGN.md`:
every candidate names its proven production/J1 reference, states what
stays identical, and lists only the changes this league's EDA justifies
(each tied to a numbered finding). Features only from FEATURES.md §1.
Per-league engine under `league/NO-OBOSLigaen/engine/<market>/`, seeded
from the NO-Eliteserien engine of the same market (itself seeded from
the J1 engine, itself from production), with the line/season retargets
this league's dev distribution requires, and the input reductions this
league's thin feed forces (no xG, no shotmap, possession-only corners
covariates — each recorded per candidate).

## Shared validation frame (all candidates)

- **Dev**: walk-forward over seasons 2022–2025 (2021 is warm-up /
  initial training, never scored). Count markets: per-match
  predict-then-update. Goals: season-blocked expanding fits (one fit
  per target season from matches strictly before it), as G-J1.
- **Virgin**: season **2026** (complete regular season, n=240 — 240/240
  finished, rounds 1–30, last match 2026-11-08; the play-offs are a
  separate competition absent from this feed in every season), read
  **ONCE**, only for arms that pass the dev gate; if NO arm passes
  dev, the virgin is NOT read.
- **Baselines**: league base rate (prior-seasons over-rate at the
  primary line, constant within a season) and naive trailing-10 (count
  markets) / climatology (goals).
- **Gate Zero**: the unmodified reference architecture, fitted per
  league, is itself an arm.
- **Gate legs (verbatim, frozen for every candidate)**: Dev gate —
  pooled dev LL at the primary line beats BOTH baselines, else arm
  dead, no virgin read. Virgin legs — (i) LL ≤ Gate Zero's and ≤ best
  baseline's; (ii) calibration |mean P(over) − actual| ≤ 1.0pp, SE
  reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev
  per-season sign check for both-pass (variant's dev LL ≤ Gate Zero's
  in at least half the dev seasons). Both-pass: lowest pooled virgin
  LL ships; ties → simpler arm. If Gate Zero fails its own dev gate,
  the candidate verdict is FAIL regardless of variant dev numbers and
  the virgin is not read.
- **Primary lines** (from the dev distribution — the ladder line whose
  dev over-rate is closest to 50%; dev n=960 matches, 959 with stats
  targets): goals OU **2.5** (over 62.19%), SOT **9.5** (47.13%),
  corners **10.5** (48.59%), cards **3.5** (38.65%; the 2.5 line sits
  at 63.02% — 3.5 is closer to 50%), total shots **20.5** (48.28%).
- **Format**: all matches are regular-season (Phase 1); no phase
  filter anywhere. Halves presentation: goals + cards FT + 1H/2H via
  the frozen F3 constants (0.440 / 0.306), presentation only; SOT,
  corners and total shots are FT-only (no halves source exists).
- **Feed caveats carried into every read**: the 2024 counting-regime
  jump (F9) spans the SOT/total-shots dev window; the virgin season's
  goals level (3.79) is far above dev (F1). Neither is corrected; the
  gates judge the models as built.

## 1. G-NO-OBOS — goals (1X2 / OU / BTTS / DC)
Reference: production Dixon-Coles pattern via the J1 engine `goals/`
(hl=270, rho grid — frozen constants as G-J1), **goals-only**
observation (X1: no xG exists; the blend's documented fallback is the
whole fit, as G-J2/G-J3).
Arms: **Gate Zero**; **SHR** — thin-team shrinkage (for a team with
fewer than 8 training-window matches, its predicted lambdas are
shrunk 50% toward the league-mean lambda — the template-sanctioned
response to the G-J2 post-mortem; the thin teams here are entrants
from 2. divisjon with no parent corpus, F4); **X2** — SHR plus the
mover tier offset for Eliteserien-relegated entrants (X2, F4:
offset estimated inside the dev fit from transitions completed before
the target season; attack/defence prior shift for the entrant's first
season only).
Forbidden: halves modelling (F3), finishing/form (F6), absence (F10),
snapshot features, imported tier offsets (R14).

## 2. S-NO-OBOS — shots on target
Reference: `model_sot.py` v5 via the NO-Eliteserien engine `sot/`
(joint ridge Poisson + total-shots component + Beta-Binomial ratio +
naive ensemble, NB r=79.94 frozen). The total-shots component reads
the stats feed's `total_shots` (the only shots input this league has;
no shotmap exists or is needed by the pattern).
Arms: **Gate Zero**; **RS** — ratio prior P 200 → 20,000 (tests how
much team ratio variation to keep). **No X4/X6 arms**: no shotmap
(F5/F7 — dropped at the feature step).
Forbidden: as G-NO-OBOS plus defensive xGOT (R5), two-stage generative
distributions (V11 stands).

## 3. C-NO-OBOS — corners
Reference: `model_corners_v3` via the NO-Eliteserien engine `corners/`
(ratings + NB total + territorial multiplier), with the multiplier
reduced to the **possession covariate only** (X9-possession, F2/FEATURES
§1 — big_chance does not exist in this feed; RU-1Division precedent).
**Primary line 10.5** (dev mean 10.71 corners).
Arms: **Gate Zero** (possession multiplier); **PLAIN** — the same
ratings + NB architecture with the territorial multiplier removed
(ablation: does the possession multiplier earn its place in a league
where it is the only covariate?). No X7 arm (no box touches, F5).

## 4. K-NO-OBOS — cards (yellows)
Reference: `model_cards.py` via the NO-Eliteserien engine `cards/`
(team card ratings, count distribution; referee not used in
production).
Target: **event-unified yellows** (Yellow + YellowRed events) — the
only target that exists: the stats feed carries no yellow_cards key
in any season, so no stats target and no stats-vs-events artefact
comparison are possible (PREPROCESSING rule 7). Reds excluded.
Primary line **3.5** (dev mean 3.19 event yellows, dev over-rate
38.65% — closer to 50% than 2.5's 63.02%).
Arms: **Gate Zero**; **X8** — referee covariate (X8, F8 r=0.715, the
program's strongest referee reading; coverage 95.4% in the virgin
season). Binding conditions as K-J1: must beat Gate Zero on dev;
fixtures without a named referee fall back to the base arm (no
imputation).

## 5. T-NO-OBOS — total shots
Reference: the shots family via the NO-Eliteserien engine
`total_shots/`. **Primary line 20.5** (dev mean 20.9 in the mixed
regime; dispersion 2.03 pooled — the highest of any OBOS market, and
the trailing-r question is live here).
Arms: **A** — v1 pattern (ratings + NB + naive ensemble, frozen r
from the dev fit); **C** — E9 mechanism (NB r from a trailing window,
league-level). Built ahead of the top-5 prospective verdict under the
same user order recorded for T-J1 (different corpus, different virgin
window, no shared fitting; the top-5 trial is untouched).

## 6. Global forbidden list
Inherited from J1 MODEL_DESIGN §7 as amended (per-league engines are
the rule; divergence only as this design justifies, through this
league's gate). Half-share modelling, absence features, finishing /
conversion / on-target-rate form features, two-stage generative SOT,
post-match snapshot features, and any feature without a reliability
check are forbidden for every candidate above.
