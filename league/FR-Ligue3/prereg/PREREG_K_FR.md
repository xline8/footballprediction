# Pre-registration — K-FR (FR-Ligue3 cards / yellows): NOT BUILT

Frozen: 2026-11-10, before any fitting. Design authority:
`analysis/MODEL_DESIGN.md` (K-FR); evidence EDA F1/F5.

K-FR is **not built**, by feasibility, recorded here so the absence
is an auditable decision and not an omission:

- The stats yellows target exists in NO season at all: the stats
  feed carries no `yellow_cards` / `red_cards` key in any of the
  1,570 payloads (0 matches with a stats feed in 2021/2022–2026/2027).
- The event-feed fallback target is not consistent across the dev
  era: plain Yellow Card events exist ONLY from 2023/2024 onward
  (2021/2022–2022/2023: 0 plain Yellows in 574 event matches; only
  plain Red 74/62 and YellowRed 22/31). A yellows target defined on the
  event feed would have no dev window in 2021/2022–2022/2023 and a
  two-season target from 2023/2024 — a target-definition break, not a
  modelling window. No trait reliability is measurable on a
  consistent dev target, and no 1H share is computable on dev as a
  frozen constant (the 2023/2024-onward event-yellows 1H share 0.3580 is
  recorded in EDA F3, not frozen).
- Referee data is absent in dev (named in 0/1,570 matches, every
  season), so no X8 referee arm exists.
- No arm, window, or line is therefore frozen, nothing is fitted,
  and the virgin is not read for yellows. The frozen split
  (dev ≤ 2024/2025, virgin 2025/2026, 2026/2027 untouched reserve) is NOT moved to
  manufacture a dev window. If future seasons add a consistent
  yellows feed in dev, K-FR can be pre-registered fresh — it may
  not be rescued inside this prereg.

Verdict: `reports/K_FR_VERDICT.md` (not-buildable).
