# Phase 3.5 — Data Processing / Feature Engineering (MX-ExpansionMX)

Consumption rule (program-wide): MODEL_DESIGN.md may use only the
features defined in §1, plus the architectural components in §2.
Everything in §3 is rejected with its reason and may not re-enter.
The global causality contract of the J1 FEATURES.md applies
verbatim (strictly pre-match windows; trailing or expanding-with-
decay; ratio features are ratios of sums; NaN ⇒ arm inactive,
never silently filled; fitted state never uses post-kickoff data).

## §1 Accepted features

### X5-analogue — Trailing target-rate means (cards naive / ensemble component)
- Definition: the production cards architecture's own components —
  decayed venue-split team yellow ratings (HL=270, K=8 shrinkage)
  and the trailing-10 naive means, exactly as in `model_cards.py` /
  the J1 cards port. Source: unified event yellows (this league's
  only cards source).
- Availability: clean cards era only (2023/2024 - Apertura on).
- Justification: yellows trait reliability for r=0.957 / against
  r=0.934 in this league's EDA + the reference architecture's own
  validation history.

### Goals architecture inputs (not features — the reference pattern itself)
- Per-match goals (header score) entering the Dixon-Coles fit with
  exponential decay hl=270. Goals trait reliability for r=0.909 /
  against r=0.948 justifies per-league DC fitting.

## §2 Architectural components (delimited)

- Dixon-Coles estimation with production rho grid and tau
  correction (goals), goals-only observation.
- Cards: decayed venue-split ratings + NB total with r estimated
  on the warm-up block, per the production cards pattern.
- Halves presentation via frozen constants (goals 0.448, yellows
  0.402) — presentation only, never fitted.

## §3 Rejected features (each with its measured reason)

- **X1 blend pair (xG)** — DROPPED: xG exists in 0 of 1,208
  modelling-corpus payloads (stats era = in-progress 2026/2027
  only). Goals observation is goals-only.
- **X2 mover tier offset** — DROPPED, settled with reasons: this
  league has NO promotion to Liga MX and receives NO relegation
  from it (suspended since 2020; the league is a closed
  development tier). Measured: same-block team-id overlap with the
  Liga MX corpus = 0 in all 10 blocks; the only entrants (3
  team-blocks) are franchise entries (Alacranes de Durango,
  Atlético La Paz, Irapuato), not parent-corpus movers. There is
  no parent-corpus arm to build.
- **X3 set-play xG share** — DROPPED: no xG in the corpus (X1).
- **X4 xG per shot** — DROPPED: shotmap empty in all 1,208
  modelling-corpus payloads.
- **X6 attacking xGOT** — DROPPED: no shotmap (X4).
- **X7 box touches (corners covariate)** — DROPPED: no stats era;
  corners are not a candidate at all in this build.
- **X8 referee strictness** — DROPPED: referee named on 0% of dev
  matches (first coverage: 12.4% in the virgin block, 84.2% in the
  excluded in-progress season). No dev window exists for it.
- **X9 possession / big-chance (corners covariates)** — DROPPED:
  no stats era.
- **R7 altitude** — REJECTED after measurement: home edge at
  ≥2,000 m is +0.207 (n=150) vs +0.513 for the rest (n=1,058) —
  no positive altitude effect exists in this league's data (the
  Liga MX descriptive +0.586/+0.221 does not transfer; PE measured
  none either). Per the standing rule it could only enter via a
  pre-registered arm; none is registered, because the measurement
  gives it nothing to explain.
- Half-share modelling, finishing/conversion traits, lineup/
  absence features, standings/h2h snapshots: rejected program-wide
  (J1 §3) and unmeasurable here in any case.

## Frozen halves constants (presentation only)

| Market | 1H share | Source |
|---|---|---|
| Goals | 0.448 | event goal times, n=1,207, true variance 0.0 |
| Yellows | 0.402 | clean cards era, n=630 |
| SOT / corners / total shots | null | no era — markets not buildable |
