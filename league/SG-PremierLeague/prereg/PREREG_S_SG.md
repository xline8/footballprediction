# Pre-registration — S-SG (SG-PremierLeague shots on target): NOT BUILT

Frozen: 2026-11-10, before any fitting. Design authority:
`analysis/MODEL_DESIGN.md` (S-SG); evidence EDA F1/F2/F3/F6.

S-SG is **not built**, by feasibility, recorded here so the
absence is an auditable decision and not an omission:

- The SOT target exists in NO season at all: the stats feed
  carries no `ShotsOnTarget` key in any of the 555 payloads
  (0 matches with a stats feed in 2021–2026/2027; 0 in dev, 0
  in the virgin, 0 in the reserve). There is no dev season, no
  warm-up season, and no scored dev window at all before the
  virgin season (2025/2026) itself.
- Trait reliability is not measurable on dev (split-half r
  null, n = 0 teams — the target is absent in every dev
  season), and no 1H share is computable on dev (0 matches
  with FirstHalf/SecondHalf splits in dev), so no line can be
  selected and no halves constant frozen.
- No arm, window, or line is therefore frozen, nothing is
  fitted, and the virgin is not read for SOT. The frozen split
  (dev ≤ 2024/2025, virgin 2025/2026, 2026/2027 untouched
  reserve) is NOT moved to manufacture a dev window:
  re-splitting after seeing the era break would be post-hoc
  window shopping. If future seasons add dev-era stats
  seasons, S-SG can be pre-registered fresh — it may not be
  rescued inside this prereg.

Verdict: `reports/S_SG_VERDICT.md` (not-buildable).
