# Step 6 — Model design: VE-PrimeraDivision

No model is fit in this brief. This document freezes the feasible
candidates, windows, lines, and gate arithmetic for pre-registration.

## Feasibility and windows

| market | seed / training | dev scored | virgin / confirmatory | primary line |
|---|---|---|---|---|
| G-VE | 2021+2022 regular, n=492 | 2023–2024 regular, season blocks, n=392 | 2025 regular n=182 (complete); 2026 regular reserved confirmatory | OU 2.5 plus 1X2 |
| S-VE | 2025 Clausura regular, n=91 | 2026 Apertura regular, blocks R1–7 (n=49) + R8–13 (n=42) | 2026 Clausura regular n=91, TRANSITIONAL (complete phase; season in progress) | 8.5 |
| C-VE | 2025 Clausura regular, n=91 | 2026 Apertura regular, n=91 | 2026 Clausura regular n=91, TRANSITIONAL | 8.5 |
| K-VE | 2025 Clausura regular, n=91 (yellows in 62 — full-feed matches only) | 2026 Apertura regular, n=91 | 2026 Clausura regular n=91, TRANSITIONAL | 6.5 |
| T-VE | 2025 Clausura regular, n=91 | 2026 Apertura regular, n=91 | 2026 Clausura regular n=91, TRANSITIONAL | 24.5 |

Count lines are computed ONLY from the dev distribution (2026
Apertura regular): means and over-rates are SOT 8.2527 / 34.07% at
8.5, corners 8.7363 / 50.55% at 8.5, stats yellows 6.1648 / 42.86%
at 6.5, total shots 24.6374 / 50.55% at 24.5. No virgin-window value
sets a line. Goals dev (2023+2024 regular): mean 2.4031, OU2.5
over-rate 43.88%, home-win rate 42.86%.

Known before any fitting (descriptive CSV summaries, NOT used to set
lines — the BO 2025-goals-spike precedent): the virgin window sits
at materially higher count levels than the dev window (2026
Clausura regular means: SOT 9.23, corners 9.37, total shots 28.40;
yellows lower at 5.01). The drift builds month by month through
2026, so the virgin calibration legs are expected to be hard — the
gate decides, and the window is not moved because the outcome is
inconvenient. The goals virgin (2025 regular, 2.335 goals/match) is
NOT an outlier versus the dev window (2.403).

Why these windows: no complete stats-era virgin season exists yet
(stats start 2025-07-04). The most recent complete phase — 2026
Clausura first stage (91 regular matches, played 2026-07-31 to
2026-10-18) — is the virgin, marked TRANSITIONAL like J1's 2026:
the Clausura Quadrangular (round 6), Clausura Final and Super Final
are still pending, and a season-end confirmatory read is outstanding.
Dev is the immediately preceding complete phase (2026 Apertura) so
the temporal order is clean (Apertura Final 2026-06-07, Clausura
starts 2026-07-31). The rejected alternative — dev = 2025 Clausura
rounds 7–13 scored off a rounds 1–6 seed (n=42, ~3 matches/team) —
was discarded: the seed is too thin for ratings. Playoff rows
(phase=playoff) never enter any fit or scored window, for any market.

## Candidates

G-VE is goals-only Dixon–Coles Gate Zero (production `model_v2.py`
pattern, hl = 270), with a pre-registered SHRINK arm for
new-team/opening-match instability (the sanctioned G-J2-lesson arm).
Primary scoring is 1X2 log loss and RPS versus climatology, plus
OU2.5 log loss versus the league base rate.

S-VE is Gate Zero v5 without xG inputs (none exist), plus an RS arm
(Beta-Binomial prior 20,000 — the AU/SA-winning configuration). RS is
the v5-component test, not an EDA-motivated arm: the on-target rate
is noise here (split-half r=−.300 pooled), so hardening the prior
toward the league mean is the direction the evidence points; RS ships
only if it beats Gate Zero on dev and virgin.

C-VE is Gate Zero only (production `model_corners_v3` pattern, X9
covariates: trailing possession live, big-chance void — constant 0).
No variant arm exists: X7 is impossible (no box-touch key).

K-VE is Gate Zero only (production `model_cards.py` pattern), with
the STATS-yellows target (`yellow_cards` from the stats feed). No
variant arm exists: X8 is dropped.

T-VE has arms A/B/C: v1 (ratings + NB + naive ensemble), v2 (A plus
the level layer), and E9 (NB dispersion r from a trailing window —
single-league analogue: up to the 200 most recent stats-era matches,
all available history when fewer; minimum 50 trailing matches, else
the arm falls back to v1's fitted r for that block). The top-5
prospective v2-vs-E9 trial is untouched and neither result
contaminates the other (different corpus, different virgin window,
no shared fitting).

Halves are FT plus 1H/2H presentation using the frozen constants in
EDA (goals .4478, SOT .4651, corners .4669, total shots .4662,
stats yellows .3900); they are never separate fitted targets.

## Gate frame

The dev gate is pooled dev log loss at the primary line beating both
baselines: the league base rate at that line and naive trailing-10.
For goals, 1X2 LL and RPS must beat climatology, and OU2.5 LL must
beat its base-rate baseline. If Gate Zero (or arm A for T-VE) fails
dev, variants are moot and the virgin is not read.

For a virgin leg, LL must be no worse than Gate Zero (arm A for
T-VE) and both baselines. Calibration is `actual − predicted`;
absolute mean calibration ≤1.0 percentage point is a clean PASS, a
breach within 1 SE is PROVISIONAL PASS, and beyond that is FAIL.
Variant arms require a per-block dev sign check. If multiple arms
pass, the lower virgin LL ships; ties go to the simpler arm. A
failed gate ships nothing.
