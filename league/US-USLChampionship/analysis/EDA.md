# Stage A — EDA: USA USL Championship

All headline values below come from `eda_summary.json`; 2026 is excluded
except for the explicitly labelled inventory note. The modelled pooled
sample is 2,203 matches (2021–25); dev is 2022–24 (n=1,318) and virgin
is 2025 (n=375).

## Findings

**F1 — Levels drift down; the virgin season is a low regime.** Goals by
season: 2.878, 2.936, 2.752, 2.643, 2.635. Pooled home/away goals are
1.567/1.213, a +0.353 home edge (US-MLS: +0.456). Pooled SOT/corners/
shots/yellows are 8.433/9.244/24.162/4.325 — every count level sits
below US-MLS (9.119/9.833/25.610/4.047 except cards, which run higher
here). The virgin season 2025 is the lowest-scoring, lowest-shooting
season in the corpus (goals 2.635, SOT 7.656, shots 22.771): count
models fitted on dev will tend to over-predict it, which is exactly
what the virgin calibration leg exists to catch.

**F2 — Core traits are reliable.** Split-half r: goals-for .633,
goals-against .685, shots-for .716, SOT-for .652, corners-for .585,
yellows-for .759 (the strongest card trait in the US pair; US-MLS
.571), big-chance-for .592. All clear the adoption screen comfortably.

**F3 — Halves constants are frozen, not team features.** On complete
2024–25 period-split matches (n≈730–798), first-half shares are goals
.459, SOT .456, corners .460, shots .453, yellows .369; true variances
are −.0042, −.0026, +.0022, +.0009, +.0032 respectively — at or near
noise for goals/SOT, small for the rest. These are presentation
constants only. The 2023 subset gives similar shares (.468/.467/.452/
.459) except yellows (.299, on a partial-split sample) — the constants
are frozen from the complete 2024–25 era only.

**F4 — No mover tier exists; churn is contraction/expansion.** USL has
no relegation. Post-2021 first-season goal difference per match for
genuinely new team_ids: Detroit City +0.34 (2022, n=35), Monterey Bay
−0.50 (2022, n=34), North Carolina +0.29 (2024 returning, n=35),
Rhode Island +0.45 (2024, n=38), Lexington −0.37 (2025, n=30). Mixed
signs, small samples: no systematic expansion penalty is measurable,
so no tier offset is estimated. The thin-history problem itself is
real (Lexington enters the virgin season with zero corpus history)
and is handled by the pre-registered SHR shrinkage arm in G-USL,
exactly as in US-MLS.

**F5 — Cards target: stats feed (artefact is in the events feed).**
See PREPROCESSING.md §6 for the full audit. Event-feed Card events are
near-absent in 2021–22; where both feeds exist (2023–25) they agree
closely. Unified yellows = stats feed.

**F6 — No xG, no shotmap, anywhere.** `expected_goals` appears in 0 of
2,590 matches and has_shotmap is false for all 2,590. Consequences:
goals runs Dixon-Coles goals-only (the production blend's documented
fallback becomes the whole fit); X3 (set-play xG), X4 (xG/shot) and
X6 (xGOT/shot) are dropped by design, not by reliability failure;
the SOT v5 architecture runs without its quality-input arms, leaving
Gate Zero + the RS ratio-shrink arm.

**F7 — Referee strictness is real but modest.** Split-half r = .378
across 31 referees with ≥20 modelled matches (n=1,626 named-referee
matches). Coverage is 0% in 2021 (warm-up only), then 98.7% / 97.2% /
91.7% in dev 2022–24 and 96.3% in virgin 2025. r = .378 is well above
the noise floor that killed X8 in IT-SerieB (r = .061) and below
US-MLS (.634): X8 is adopted as an arm and the dev gate decides.

**F8 — Territorial traits are reliable; box-touch coverage ramps.**
Box-touches-for/against split-half r = .556/.495; per-match corner
correlation is .514 with box touches versus .305 with possession
(n=2,462 team-matches) — nearly identical to US-MLS (.513/.343).
Coverage ramps 21%→34%→39%→100%→100% (2021–25), so the X7 arm needs
the min-8 trailing rule with Gate Zero fallback, as in US-MLS.

**F9 — Dispersions.** Variance/mean: goals 1.069, SOT 1.152, corners
1.225, shots 1.464, yellows 1.368. Total shots are the most
overdispersed count (US-MLS 1.325): the E9 trailing-r arm question is
live for T-USL.

**F10 — Dev primary-line screen (over-rates, dev 2022–24 pooled).**
Goals OU2.5 .526; SOT 8.5 .483 (7.5 → .605, 9.5 → .362); corners 9.5
.451 (8.5 → .577, 10.5 → .332); cards 4.5 .541 (3.5 → .697, 5.5 →
.361); total shots 24.5 .476 versus 25.5 .407 (23.5 → .552, 26.5 →
.341). Primary lines frozen in MODEL_DESIGN.md from this screen:
2.5 / 8.5 / 9.5 / 4.5 / **24.5** (shots takes the line closest to a
0.5 dev over-rate, the IT-SerieB T precedent).
