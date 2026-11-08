# Phase 3 — EDA: ES-LaLiga2

All numbers computed by `analysis/eda_compute.py` from the built CSV
(raw dump: `analysis/eda_numbers.json`; churn/mover blocks keyed on
team_id / accent-normalised names after the coordinator caught the
raw-name phantom-club artefact — see DATA_UNDERSTANDING §1).
Complete seasons only for pooled rates unless stated. J1/DK/ENGCH
checklist replicated.

## Levels per season (per match, both teams)

| Season | Goals | xG | SOT | Corners | Shots | Yellows (events) | Yellows (stats) | Reds |
|---|---|---|---|---|---|---|---|---|
| 2021/2022 | 2.421 | — | 8.011 | 9.299 | 24.132 | 4.658 | 4.109 | 0.207 |
| 2022/2023 | **2.017** | — | 7.188 | 9.222 | 22.440 | 4.991 | 4.524 | 0.299 |
| 2023/2024 | 2.233 | — | 7.571 | 9.308 | 24.006 | 4.707 | 4.562 | 0.199 |
| 2024/2025 | 2.543 | — | 8.246 | 9.325 | 24.338 | 4.716 | 4.596 | 0.259 |
| 2025/2026 (virgin) | 2.626 | 2.717 | 8.637 | 9.423 | 25.143 | 5.100 | 5.026 | 0.284 |
| 2026/2027 (partial, n=138) | 2.746 | 2.832 | 8.783 | 9.391 | 26.384 | 5.420 | 5.326 | 0.254 |

(xG shown only where the key exists — 2025/2026 onward; the 1–3
xG-carrying matches in dev seasons are not a level.)

F1 — This is a **low-scoring, low-corner** league with **high cards**:
goals 2.02–2.54 in the dev era (the 2022/2023 season at 2.017 goals
is an extreme low — the coordinator's independent recount from the
index scores confirms it exactly; it is a property of that season,
not a data error), corners ≈ 9.3 (ENGCH 9.7–10.6), SOT ≈ 7.2–8.2,
shots ≈ 22.4–24.3, event yellows ≈ 4.7–5.0 per match — a card-heavy
league by program standards. Levels drift substantially season to
season (goals range 0.53 across dev seasons), which justifies
per-league fitting with time decay. The virgin season ran **hot on
every market** (goals 2.626, OU2.5 over-rate 50.2% vs dev 40.0%; SOT
over-7.5 60.5% vs 49.1%; shots over-23.5 59.2% vs 48.1%; cards
over-4.5 58.8% vs 53.6%) — the gates' calibration legs will meet
that regime as it is. The partial 2026/2027 runs hotter still (small
n, early season) and stays a reserved confirmatory window, never a
design input.

## Home advantage & base rates (complete seasons pooled, n=2,340)

- Home goals 1.358 vs away 1.010 per match; pooled home edge
  **+0.348 goals** (ENGCH +0.285, SCO +0.38). Home-win rate 44.9%;
  dev OU2.5 over-rate 40.0%.

## F2 — Team trait reliability (career-pooled split-half, 39 teams with ≥10 matches)

| Trait | r | Verdict |
|---|---|---|
| possession | 0.899 | SIGNAL |
| big-chance-for | 0.761 | SIGNAL |
| box touches-for | 0.707 | SIGNAL |
| box touches-against | 0.659 | SIGNAL |
| SOT-for | 0.641 | SIGNAL |
| shots-for | 0.628 | SIGNAL |
| corners-for | 0.553 | SIGNAL (moderate) |
| goals-for | 0.501 | SIGNAL (moderate) |
| yellows-for (events) | 0.453 | SIGNAL (moderate) |

Reliabilities sit below the big-league programmes (SCO 0.90+) and
near ENGCH's: with 32% of the league replaced every season and 42
clubs cycling through, career traits are diluted by churn — the
mover problem the goals design must face. In contrast to ENGCH
(yellows-for r = −0.01), the ES yellows trait **is** real (0.453):
the cards candidate has a genuine team-trait base here.

## F3 — Half shares: frozen-constant question

Measured on the complete-splits era 2023/2024–2025/2026 (stats-based
n≈1,403; goals and yellows via events):

| Market | 1H share | True SD of per-match share |
|---|---|---|
| goals | **0.4322** | 0.000 |
| SOT | **0.4491** | 0.033 |
| corners | **0.4692** | 0.048 |
| total shots | **0.4522** | 0.017 |
| yellows (events) | **0.3455** | 0.069 (cards stay back-loaded; constant still the only mechanism) |

Verdict (same as J1/DK/ENGCH): per-match 1H share variance is ≈
sampling noise around a league constant. **Frozen constants only**
(table above), presentation only.

## F4 — Mover tier offsets (the Segunda's central question)

Entry-season performance of clubs whose previous season was in the
adjacent tier (warehouse team lists for LaLiga id 87 / Primera
Federación id 8968, accent-normalised name matching; pooled over the
five entry seasons 2022/2023–2026/2027; exactly 3 + 4 movers every
season):

| Entry source | team-matches | GF/match | GA/match | GD/match | ΔGF vs mu 1.191 | ΔGA vs mu |
|---|---|---|---|---|---|---|
| from LaLiga | 558 | 1.271 | 1.020 | **+0.251** | **+0.080** | **−0.171** |
| from Primera Federación | 723 | 1.166 | 1.302 | **−0.136** | **−0.025** | **+0.111** |

**SIGNAL, asymmetric and defence-led**: a relegated LaLiga club is,
on entry, a quarter-goal per match better than the average Segunda
club — almost all of it defensive (GA −0.171; GF only +0.080; no
ENGCH-style parachute attack premium). A promoted third-tier club's
problem is likewise defensive (GA +0.111, GF −0.025). These
magnitudes freeze the X2 arm's offsets in PREREG_G_ES (ENGCH F4
pattern: descriptive magnitudes, applied only at prediction time in
the mover's entry season).

## F5 — Set-play xG share reliability: **NOT MEASURABLE** — the xG
   splits exist in 7 of 1,872 dev matches; the era starts inside the
   virgin. X3 dropped on availability (FEATURES). No number is
   quoted: inventing one from the virgin would contaminate it.
## F6 — xG per shot reliability: **NOT MEASURABLE** — shotmap exists
   in 7 of 1,872 dev matches. X4 dropped on availability.
## F7 — xGOT per shot: **NOT MEASURABLE** in the dev window (same era
   break). X6 dropped on availability.
## F8 — Referee yellow rate reliability: r = **0.180** on dev seasons
   (38 referees with ≥10 matches); r = 0.269 pooled over complete
   seasons (43 referees) — **NOISE** by the program's standard
   (J1 0.65, DK 0.56; ENGCH dropped X8 at 0.259). Referee coverage
   is also 48.5% in the seed season and 82.1% in the virgin. X8 is
   dropped in FEATURES; K-ES runs Gate Zero only.
## F11 — xG calibration: not applicable to any arm (no xG arm).
   Descriptively, in the only era where xG exists, goals/xG is
   0.966 (2025/2026) and 0.970 (2026/2027 partial) — recorded for a
   future prereg if the xG era ever gains a dev window.

## Feasibility summary

Goals exist in 100% of matches; SOT / corners / total shots exist in
the stats feed in 100% of matches in every season; the unified
(event) yellows target exists in 100% of matches; the virgin season
contains all five targets → **five candidates** (MODEL_DESIGN). The
era break removes only the xG-consuming *arms*, not any candidate.
