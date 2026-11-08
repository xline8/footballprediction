# Pre-registration — G-EE (EE-Meistriliiga goals model)

Frozen: 2026-11-10, before any fitting. Phase A only; no engine or results
exist yet. Design authority: `analysis/MODEL_DESIGN.md`; data evidence:
`analysis/EDA.md` and `analysis/FEATURES.md`.

## Reference architecture

- Production Dixon–Coles `model_v2.py` class `DC`: 14 sweeps, damping 0.7,
  +0.25 smoothing, fitted home advantage, attack/defence ratings, MAXG=10,
  production tau low-score correction.
- Rho grid is production: (0.0, −0.05, −0.10, −0.15), selected by weighted
  goals log-likelihood. Time decay is `0.5 ** (age_days / 270)`; hl=270 is
  frozen.
- X1 is goals-only. xG is absent in all 1,056 payloads, so no blend value is
  ever available.
- Target-season fit uses every match dated strictly before that season’s first
  match. Unseen teams start at league mean (attack=defence=0).

## Arms

1. **Gate Zero** — the unmodified reference architecture.
2. **SHRINK** — Gate Zero plus thin-history rating shrinkage. For a team with
   n prior in-league matches at prediction time and n < 6, multiply both its
   fitted attack and defence ratings by `n / (n + 6)`; for n >= 6 use 1.0.
   Unseen teams remain at zero. k=6 and threshold n<6 are frozen.
3. **X2** — Gate Zero plus entrant offset. An entrant is a team id absent from
   the immediately preceding season and present in target season S; for 2022,
   the preceding season is the partial 2021 corpus. At prediction time in its
   first season only, add attack `log(max(mu + dGF_S, 0.10) / mu)` and
   defence `log((mu + dGA_S) / mu)`, where mu is the decay-weighted mean
   goals per team-match in the training window and (dGF_S, dGA_S) is the
   frozen expanding pooled entrant deviation over entrants in seasons
   strictly before S — 2023: (−0.358333, +1.030556); 2024: (−0.440278,
   +0.726389); 2025: (−0.588889, +0.716667); 2026 (virgin): (−0.498611,
   +0.626389). X2 is inactive for target season 2022 (no prior entrant
   exists; X2 ≡ Gate Zero that season). The all-entrant pooled figure
   (dGF −0.381111, dGA +0.641111 over 180 team-matches) is descriptive
   only and is NOT used: it includes the 2026 virgin-season entrant's own
   outcomes, which must never enter an offset applied to virgin predictions.

## Dev protocol

Warm-up is 2021 (partial); scored dev seasons are 2022, 2023, 2024 and 2025.
Walk-forward is expanding and season-blocked: one fit per target season, with
all matches strictly before that season’s first match. Pooled metrics are 1X2
natural-log loss, RPS (H/D/A order), and OU2.5 binary log loss. Climatology is
the pooled pre-target outcome/base-rate history. No 2026 rows may be read by
the dev harness.

## Virgin protocol

Virgin is complete 2026 (180 matches, ending 2026-11-07). The fit uses all
matches before the first 2026 match; virgin climatology uses 2021–2025. Read
virgin data once after dev results are frozen. Report home-win and OU2.5
calibration differences with `sd(pred-y)/sqrt(n)` standard errors.

## GATE LEGS (verbatim, frozen)

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's, (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp for home-win rate and OU2.5 over-rate, breach within 1 SE is PROVISIONAL PASS else FAIL, (iii) per-season sign check for variants. Both-pass rule: lower pooled virgin 1X2 LL ships; if none passes, G-EE FAIL and nothing ships.

## Outputs

- Engine: `league/EE-Meistriliiga/engine/goals/`.
- Dev results: `results_dev.json` and fitted parameters under that engine.
- Virgin predictions CSV: one row per 2026 match.
- Verdict: `reports/G_EE_VERDICT.md`.

This document is a frozen preregistration. Nothing is fitted in Phase A.
