# Pre-registration — K-BY (BY-PremierLeague cards): NOT BUILT

Frozen: 2026-11-10, before any fitting. Design authority:
`analysis/MODEL_DESIGN.md` (K-BY); evidence EDA F1/F2/F3/F5/F6.

K-BY is **not built**, by feasibility, recorded here so the absence
is an auditable decision and not an omission:

- No yellows target exists in ANY season at all: the stats feed
  carries no `yellow_cards` / `red_cards` key in any of the 1,394
  payloads (0 matches with a stats feed in 2021–2026), and the event
  feed carries ZERO plain Yellow events in every season (0 in dev,
  0 in the virgin, 0 in the reserve; only YellowRed + Red events
  exist). This is stronger than a definition break across eras: there
  is no yellows target to model in the first place.
- Referee coverage is 0% in every season, so no X8 referee arm
  exists either.
- Trait reliability is not measurable on dev (split-half r null,
  n = 0 teams), and no 1H share is computable on dev (the event
  yellows that exist are YellowRed only — 91 in the dev era — and are
  NOT a frozen constant; no K market), so no line can be selected
  and no halves constant frozen.
- No arm, window, or line is therefore frozen, nothing is fitted,
  and the virgin is not read for cards. The frozen split
  (dev ≤ 2024, virgin 2025, 2026 untouched reserve) is NOT moved to
  manufacture a dev window. If future seasons add a yellows target,
  K-BY can be pre-registered fresh — it may not be rescued inside
  this prereg.

Verdict: `reports/K_BY_VERDICT.md` (not-buildable).
