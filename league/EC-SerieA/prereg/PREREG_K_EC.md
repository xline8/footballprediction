# Pre-registration — K-EC (EC-SerieA cards): NOT BUILT

Frozen: 2026-11-10, before any fitting. Design authority:
`analysis/MODEL_DESIGN.md` (K-EC); evidence EDA F3/F5,
FEATURES.md X8.

K-EC is **not built**, by feasibility, recorded here so the absence
is an auditable decision and not an omission:

- There is no cards target in any dev season under EITHER source.
  Stats-feed yellows exist only from 2025 (0 matches with a stats
  feed in 2021–2023, 1 match in 2024, 311/312 in 2025). The event
  feed in dev carries zero plain Yellow events (2021–2024: Red 240,
  YellowRed 170, Yellow 0) — the only dev card events are second
  yellows, the wrong target, so there is no event-feed fallback
  either (unlike leagues where the event feed carries cards in dev).
- Trait reliability is not measurable on dev (split-half r null,
  n = 0 teams), no 1H share is computable on dev (0 matches with
  period splits in dev; event-time 1H yellows are not derived —
  dev card events are YellowRed only), and the X8 referee covariate
  cannot be measured on dev (no referee field populated in any dev
  match; named referees only from 2025, 73/312). No line can be
  selected and no halves constant frozen.
- No arm, window, or line is therefore frozen, nothing is fitted,
  and the virgin is not read for cards. The frozen split is NOT
  moved to manufacture a dev window. If future seasons add a dev
  cards target, K-EC can be pre-registered fresh — it may not be
  rescued inside this prereg.

Verdict: `reports/K_EC_VERDICT.md` (not-buildable).
