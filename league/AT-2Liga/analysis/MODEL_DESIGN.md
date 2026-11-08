# Phase 4 — Model Design: AT-2Liga Candidates

Rules of construction inherited from `league/J1/analysis/MODEL_DESIGN.md`:
every candidate names its proven production/J1 reference, states what
stays identical, and lists only the changes this league's EDA justifies
(each tied to a numbered finding). Features only from FEATURES.md §1.
Per-league engine under `league/AT-2Liga/engine/<market>/`, seeded
from the closest sibling engine — for this thin feed that is the
RU-1Division build (goals-only DC, v5 SOT without xG arms,
possession-only corners, event-yellows cards, shots A/B/C), itself
seeded from the J1/production patterns.

## Shared validation frame (all candidates)

- **Dev**: walk-forward over seasons 2022/2023–2024/2025 (2021/2022
  is warm-up / initial training, never scored). Count markets:
  per-match predict-then-update, date-grouped. Goals: season-blocked
  expanding fits (one fit per target season from matches strictly
  before it), as G-J1/G-RU1.
- **Virgin**: season **2025/2026** (complete, n=210 — a 15-team
  season, Phase 1 §1), read **ONCE**, only for arms that pass the
  dev gate; if NO arm passes dev, the virgin is NOT read. Season
  2026/2027 is in progress and reserved as the confirmatory
  window — never read in this build.
- **Baselines**: league base rate (prior-seasons over-rate at the
  primary line, constant within a season) and naive trailing-10
  (count markets) / climatology (goals).
- **Gate Zero**: the unmodified reference architecture, fitted per
  league, is itself an arm.
- **Gate legs (verbatim, frozen for every candidate)**: Dev gate —
  pooled dev LL at the primary line beats BOTH baselines, else arm
  dead, no virgin read. Virgin legs — (i) LL ≤ Gate Zero's and ≤
  best baseline's; (ii) calibration |mean P(over) − actual| ≤ 1.0pp,
  SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev
  per-season sign check for both-pass (variant's dev LL ≤ Gate
  Zero's in at least half the dev seasons). Both-pass: lowest
  pooled virgin LL ships; ties → simpler arm. If Gate Zero fails
  its own dev gate, the candidate verdict is FAIL regardless of
  variant dev numbers and the virgin is not read. (Goals uses the
  G-RU1 form of the legs: 1X2 LL + RPS vs climatology and OU2.5 LL
  vs the base-rate baseline on dev; virgin legs (i)/(ii) read on
  1X2 LL and on home-win + OU2.5 calibration — stated in full in
  PREREG_G_AT2.)
- **Calibration sign convention**: actual − predicted, everywhere
  in this build (the RU-1 convention).
- **Primary lines** (from the dev distribution, EDA digest): goals
  OU 2.5 (dev over-rate 57.2%), SOT 8.5 (55.1%), corners 9.5
  (52.8%), cards 4.5 (58.3%; the 5.5 rate 41.3% is farther from
  50%), total shots 18.5 (47.3%; the 17.5 rate 55.6% is farther
  from 50%).
- **Format**: single regular phase; every row is an ordinary row in
  every window; no phase feature anywhere. Halves presentation:
  goals and cards via their frozen event-derived constants (F3),
  presentation only; SOT / corners / total shots FT only.

## 1. G-AT2 — goals (1X2 / OU / BTTS / DC)
Reference: production Dixon-Coles pattern via the RU-1 engine
(goals-only observation, hl=270, rho grid — frozen constants as
G-RU1). There is no blend: no xG exists (X1 dropped, F11).
Arms: **Gate Zero**; **SHRINK** — the G-RU1 construction verbatim:
at prediction time, for a team with fewer than 6 prior in-league
matches in the training window, its attack/defence ratings are
shrunk toward the league mean (`a *= n/6`, `d *= n/6`). Motivation:
F4's measured mover gaps (parent-tier clubs arrive defensively
strong; from-below entrants mildly weak) plus the G-J2 lesson.
No X2 offset arm (F4/R14: n=4/n=10 too thin to hard-code).
Forbidden: halves modelling (F3), finishing/form (F6), absence
(F10), snapshot features, imported tier offsets (R14).

## 2. S-AT2 — shots on target
Reference: `model_sot.py` v5 via the RU-1 engine (joint ridge
Poisson + total-shots component + Beta-Binomial ratio + naive
ensemble, NB r=79.94 frozen).
Arms: **Gate Zero**; **RS** — ratio prior P 200 → 20,000 (tests
the §2 ratio component, as in S-RU1/S-AT). **No X4/X6 arms**: the
data does not exist (F6/F7).
Carried caveat (F12): the 2024/2025 feed definition break sits in
the dev window and in the trailing state opening the virgin
season. Recorded in the prereg; the gates decide.
Forbidden: as G-AT2 plus two-stage generative distributions
(V11 stands).

## 3. C-AT2 — corners
Reference: `model_corners_v3` via the RU-1 engine (ratings + NB
total + territorial multiplier).
Arms: **Gate Zero only** — with the possession-only territorial
covariate (X9 reduced, F9). The big-chance component and the X7
box-touch arm do not exist in this feed; no variant is registered
and the dev gate decides whether the single arm lives.

## 4. K-AT2 — cards (event yellows)
Reference: `model_cards.py` via the RU-1 engine (team card
ratings, count distribution, naive ensemble structure).
Target: event-unified yellows (Yellow + YellowRed per team),
frozen in PREPROCESSING rule 5 — the stats feed carries no cards
key at all, so no stats target exists to disagree with.
Arms: **Gate Zero only**. **No X8 arm**: referee coverage is
0.0% (F8).

## 5. T-AT2 — total shots
Reference: the shots family via the J1/RU-1 engines.
Arms: **A** — v1 pattern (ratings + NB + naive ensemble);
**B** — v2 pattern (+ level layer); **C** — E9 mechanism (NB r
from a trailing window, league-level). Carried caveat (F12) as
S-AT2, stronger here: the target itself is the contaminated
series. The gates decide.

## 6. Global forbidden list
Inherited from J1 MODEL_DESIGN §7 as amended (per-league engines
are the rule; divergence only as this design justifies, through
this league's gate). Half-share modelling, absence features,
finishing / conversion / on-target-rate form features, two-stage
generative SOT, post-match snapshot features, and any feature
without a reliability check are forbidden for every candidate
above.
