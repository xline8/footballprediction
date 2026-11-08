# Pre-registration — T-NO (NO-2Divisjon total shots): NOT BUILT

Frozen: 2026-11-10, before any fitting. Design authority:
`analysis/MODEL_DESIGN.md` (T-NO); evidence EDA F1/F2/F3/F6.

T-NO is **not built**, by feasibility, recorded here so the absence
is an auditable decision and not an omission:

- The total-shots target exists in NO season at all: the stats feed
  carries no `total_shots` key in any of the 2,158 payloads (0
  matches with a stats feed in 2021–2026; 0 in dev, 0 in the virgin,
  0 in the reserve). There is no dev season, no warm-up season, and
  no scored dev window at all before the virgin season (2025)
  itself. (Unlike FI's T case there is no definition break to
  diagnose — the feed simply never exists here.)
- Trait reliability is not measurable on dev (split-half r null,
  n = 0 teams — the target is absent in every dev season), and no
  1H share is computable on dev (0 matches with FirstHalf/SecondHalf
  splits in dev), so no line can be selected and no halves constant
  frozen. The X6 shot-volume feature cannot be adopted (no
  `total_shots` in any season).
- No arm, window, or line is therefore frozen, nothing is fitted,
  and the virgin is not read for total shots. The frozen split
  (dev ≤ 2024, virgin 2025, 2026 untouched reserve) is NOT moved to
  manufacture a dev window. If future seasons add dev-era stats
  seasons, T-NO can be pre-registered fresh — it may not be rescued
  inside this prereg.

Verdict: `reports/T_NO_VERDICT.md` (not-buildable).
