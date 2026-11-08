# Phase 6 — Model Design: DE-3Liga Candidates

Rules inherited from the program template: every candidate names
its production reference, Gate Zero is the unmodified reference
fitted per league, variants come only from FEATURES.md adopted
arms (max 2–3 per candidate), gates are the program's frozen legs,
a FAIL is a complete outcome.

Shared frame: dev = season-blocked walk-forward over
2021/2022–2024/2025 (2021/2022 = training seed / warm-up; scored
seasons 2022/2023–2024/2025, n=1,140); virgin = 2025/2026
(n=380, COMPLETE), read ONCE and only for arms passing the dev
gate; 2026/2027 (n=130, partial) reserved un-read as the
confirmatory window. Baselines: league base rate and naive
trailing-10 (count markets) / climatology (goals). Calibration =
actual − predicted (sign convention stated in every prereg);
|error| ≤ 1pp clean PASS, ≤ 1 SE PROVISIONAL PASS, else FAIL.
Primary line per candidate = the .5 line whose dev over-rate is
closest to 0.5 (EDA F6).

**Format rule (frozen here, before any fitting, and repeated in
every prereg):** all matches are ordinary rows in every fit and
every window — this corpus has no split, no play-off groups and
no qualification matches (DATA_UNDERSTANDING §1). No phase
feature is used anywhere.

**Feasibility matrix:** goals buildable (scores complete).
SOT / corners / cards / total shots buildable: their targets exist
in every dev season AND in the complete virgin season (one
stats-missing row in the 2021/2022 seed only). Cards target =
event-unified yellows (EDA F4). No xG exists anywhere (shotmap
0/1,992), so the goals reference runs its documented goals-only
fallback and X1/X3/X4/X6 are dropped by design (FEATURES.md).

| Candidate | Reference | Primary line (dev over-rate) | Arms |
|---|---|---|---|
| G-DE3 goals | production DC (model_v2.py pattern), goals-only — NO xG blend exists in this league | OU 2.5 + 1X2 LL/RPS | Gate Zero; SHRINK (sanctioned thin-data prior). No X2 (dropped, EDA F5), no X3 (no xG) |
| S-DE3 SOT | model_sot.py v5 | **9.5** (0.458) | Gate Zero; RS ratio-shrink (P=20,000). No X4/X6 (no shotmap) |
| C-DE3 corners | model_corners_v3 | **10.5** (0.467) | Gate Zero (X9 covariates); X7 box-touch multiplier (F2 r=0.848/0.821; coverage 64.5–100%, min-8 rule governs) |
| K-DE3 cards | model_cards.py | **4.5** (0.499) | Gate Zero; X8 referee covariate (coverage 88–99% from 2022/2023; referee r=0.483, F2). Target event-unified |
| T-DE3 total shots | shots family (v1/v2/E9, as T-J1) | **26.5** (0.518) | A v1 pattern; B v2 level layer; C E9 trailing-r |

Halves presentation (frozen constants, EDA F3): goals 0.445,
SOT 0.447, corners 0.466, total shots 0.452, yellow cards 0.361 —
FT + 1H/2H presentation only, never modelled.
