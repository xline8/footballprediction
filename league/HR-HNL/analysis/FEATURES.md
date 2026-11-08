# Step 5 — Feature Engineering: HR-HNL

Consumption rule, causality contract, and rejected-feature discipline are
the programme's (see league/J1/analysis/FEATURES.md §1–§3): features are
computed only from matches strictly before the target match's kickoff,
windows are trailing or expanding-with-decay, ratio features are ratios
of sums, and a feature whose window cannot be filled is NaN with its arm
inactive — never filled from the target match's own era.

## Adopted / dropped — the J1 template X1–X9 against THIS league's data

| # | Feature | Verdict | Reason (this league's evidence) |
|---|---|---|---|
| X1 | Blend observation pair (goals + xG) | **ADOPTED as goals-only fallback** | No `expected_goals*` key in any of 964 payloads; no shotmap. The production blend's documented fallback (goals-only observations) is the only form that exists here — G-HR is a goals-only DC. |
| X2 | Entrant (promoted-club) offset | **ADOPTED** (G-HR arm) | Entrants identified in-corpus by absence from the previous season (tier-1 league; no tier-2 corpus in-system). EDA F4: n = 4 transitions, GF diff −0.380, GA diff +0.599 per match vs league team mean — the expected tilt, same signs as J1/FI. Offset estimated only from transitions completed before the predicted season, min 3, multipliers clamped [0.8, 1.25] (FI pattern). |
| X3 | Set-play xG share/rate | **DROPPED** | No xG of any kind in the feed (X1 note). Data absent. |
| X4 | xG per shot (shotmap) | **DROPPED** | `has_shotmap` False for 964/964. Data absent. |
| X5 | Trailing target-rate means (naive/ensemble inputs) | **ADOPTED** (S/C/T base) | Target traits strongly reliable in this league (EDA F2: SOT r = 0.922, corners 0.823, shots 0.897, goals 0.927). |
| X6 | xGOT per shot (era-guarded) | **DROPPED** | No shotmap, no xGOT. Data absent. |
| X7 | Opp-box touches for/against (trailing) | **ADOPTED** (C-HR arm) | Key present (720/900 complete-era matches); for-trait r = 0.925, against r = 0.853; per-match corr with corners 0.376 (EDA F5). Coverage is partial in the 2022/2023–2023/2024 dev seasons — the reference min-8-of-last-10 validity rule governs activation and the active share is reported. |
| X8 | Referee yellow rate (trailing) | **DROPPED** | Coverage is adequate (728/900 named) but the trait fails reliability in THIS league: split-half r = 0.239 (EDA F7) vs J1's 0.65. Also moot: its only consumer (K-HR) is not built (F6 artefact). |
| X9 | Territorial covariates (possession + big_chance) | **ADOPTED** (C-HR Gate Zero) | Full form — unlike FI (possession-only), both keys exist in every season here. Possession trait r = 0.949; big-chance for-trait r = 0.818 (EDA F2/F5). Carried unchanged from the production corners reference so Gate Zero is the true production pattern. |

## Halves constants (frozen, presentation only — not features)

From EDA F3, dev era only: goals 0.4320 (event times), SOT 0.4729,
corners 0.4793, total shots 0.4661 (period splits). Every built market
in this league HAS a legitimate halves source (goal/card event times in
all eras for goals; period splits from 2022/2023 for the stats markets,
with constants pooled over the dev split matches), so no market is
frozen FT-only on halves grounds. (Cards would have had a splits source
too; it is not built for the F6 target reason, not a halves reason.)

## Rejected (programme §3, applied)

Team first-half shares (R1, noise — F3 discipline), trailing finishing /
conversion (R2/R3 — no xG in any case), standalone on-target rate (R4 —
v5's internal Beta-Binomial component is architecture, not a covariate),
lineup/absence (R6, closed programme-wide), red-card rates (R12),
standings/h2h/form snapshots (R9, leakage), attendance (R10).
