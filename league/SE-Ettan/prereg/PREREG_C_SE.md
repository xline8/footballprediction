# Pre-registration — C-SE (SE-Ettan corners): NOT BUILT

Frozen: 2026-11-10 WIB, before any fitting. Design authority:
`analysis/MODEL_DESIGN.md` (C-SE); evidence EDA F1/F2/F3/F6,
FEATURES.md X7.

C-SE is **not built**, by feasibility, recorded here so the absence
is an auditable decision and not an omission:

- The corners target exists in NO season: the stats feed is 0% in
  2021–2025 (0 matches with a stats feed in any season; stats keys
  per season are empty in `eda_summary.json`). The stats era never
  starts. There is no dev season, no warm-up season, and no scored
  dev window at all.
- Trait reliability is not measurable on dev (split-half r null,
  n = 0 teams — the target is absent in every dev season), and no
  1H share is computable on dev (0 matches with FirstHalf/SecondHalf
  splits in any season), so no line can be selected and no halves
  constant frozen. The X7 opp-box-touches covariate exists nowhere
  (there is no stats feed in any season), so no touches variant has
  a dev window either.
- No arm, window, or line is therefore frozen, nothing is fitted,
  and the virgin is not read for corners. The frozen split
  (dev ≤ 2024, virgin 2025, 2026 untouched reserve) is NOT moved to
  manufacture a dev window: re-splitting after seeing the era break
  would be post-hoc window shopping. If future seasons add dev-era
  stats seasons, C-SE can be pre-registered fresh — it may not be
  rescued inside this prereg.

Verdict: `reports/C_SE_VERDICT.md` (not-buildable).
