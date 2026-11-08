# Pre-registration — K-NO (NO-2Divisjon cards / yellows): NOT BUILT

Frozen: 2026-11-10, before any fitting. Design authority:
`analysis/MODEL_DESIGN.md` (K-NO); evidence EDA F1/F5.

K-NO is **not built**, by feasibility, recorded here so the absence
is an auditable decision and not an omission:

- The stats yellows target exists in NO season at all: the stats
  feed carries no `yellow_cards` / `red_cards` key in any of the
  2,158 payloads (0 matches with a stats feed in 2021–2026).
- The event-feed fallback target is not consistent across the dev
  era: plain Yellow Card events exist ONLY from 2024 onward
  (2021–2023: 0 plain Yellows in 1,034 event matches; only Red
  35/25/22 and YellowRed 24/15/13). A yellows target defined on the
  event feed would have no dev window in 2021–2023 and a
  one-season target in 2024 — a target-definition break, not a
  modelling window. No trait reliability is measurable on a
  consistent dev target, and no 1H share is computable on dev as a
  frozen constant (the 2024-only event-yellows 1H share 0.2981 is
  recorded in EDA F3, not frozen).
- Referee data is absent in dev (named in 0/2,158 matches, every
  season), so no X8 referee arm exists.
- No arm, window, or line is therefore frozen, nothing is fitted,
  and the virgin is not read for yellows. The frozen split
  (dev ≤ 2024, virgin 2025, 2026 untouched reserve) is NOT moved to
  manufacture a dev window. If future seasons add a consistent
  yellows feed in dev, K-NO can be pre-registered fresh — it may
  not be rescued inside this prereg.

Verdict: `reports/K_NO_VERDICT.md` (not-buildable).
