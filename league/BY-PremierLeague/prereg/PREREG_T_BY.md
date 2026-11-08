# Pre-registration — T-BY (BY-PremierLeague total shots): NOT BUILT

Frozen: 2026-11-10, before any fitting. Design authority:
`analysis/MODEL_DESIGN.md` (T-BY); evidence EDA F1/F2/F3/F6.

T-BY is **not built**, by feasibility, recorded here so the absence
is an auditable decision and not an omission:

- The total-shots target exists in NO season at all: the stats feed
  carries no `total_shots` key in any of the 1,394 payloads (0 matches
  with a stats feed in 2021–2026; 0 in dev, 0 in the virgin, 0 in
  the reserve), and the shotmap is empty in every season (0 shots in
  1,394 matches), so no shotmap-derived shots target exists either.
  There is no dev season, no warm-up season, and no scored dev window
  at all before the virgin season (2025) itself.
- Trait reliability is not measurable on dev (split-half r null,
  n = 0 teams — the target is absent in every dev season), and no
  1H share is computable on dev (0 matches with FirstHalf/SecondHalf
  splits in dev), so no line can be selected and no halves constant
  frozen.
- No arm, window, or line is therefore frozen, nothing is fitted,
  and the virgin is not read for total shots. The frozen split
  (dev ≤ 2024, virgin 2025, 2026 untouched reserve) is NOT moved to
  manufacture a dev window: re-splitting after seeing the era break
  would be post-hoc window shopping. If future seasons add dev-era
  stats seasons, T-BY can be pre-registered fresh — it may not be
  rescued inside this prereg.

Verdict: `reports/T_BY_VERDICT.md` (not-buildable).
