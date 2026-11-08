# Pre-registration — S/C/K/T-FI (FI-Ykkonen SOT / corners / cards / total shots): NOT BUILT

Frozen: 2026-11-10, before any fitting. Design authority:
`analysis/MODEL_DESIGN.md` (S/C/K/T-FI); evidence EDA F1/F2/F3/F5/F6,
FEATURES.md. Split decision: Jarvis OPSI A (board comment
6761468990) — dev ≤ 2024, virgin 2025, 2026 reserve; the split is
NOT moved to manufacture a dev window for any of these candidates.

S-FI, C-FI, K-FI and T-FI are **not built**, by feasibility, recorded
here so the absence is an auditable decision and not an omission.
The virgin is not read for any of them.

## S-FI (shots on target) — not-buildable
- The SOT target exists ONLY where a stats feed exists: **0
  matches with a stats feed in every season 2021–2026 (0/1,730)**.
  No SOT column is populated in any season; shotmap 0/1,730.
- There is no dev season, no warm-up season and no scored dev
  window at all; trait reliability is not measurable on dev
  (split-half r null, n = 0 teams); no 1H share is computable on
  dev (0 matches with FirstHalf/SecondHalf splits in dev), so no
  line can be selected and no halves constant frozen.

## C-FI (corners) — not-buildable
- The corners target exists ONLY where a stats feed exists: **0
  matches with a stats feed in every season 2021–2026 (0/1,730)**.
- Same consequence as S-FI: no dev window, no trait, no line, no
  halves constant. The X7 opp-box-touches covariate is likewise
  absent in dev (it exists only in the stats era, which never
  arrives in this corpus), so no touches variant has a dev window
  either.

## T-FI (total shots) — not-buildable
- The total-shots target exists ONLY where a stats feed or shotmap
  exists: **stats 0/1,730, shotmap 0/1,730 in every season**.
- Same consequence as S-FI/C-FI: no dev window, no trait, no line,
  no halves constant.

## K-FI (cards) — not-buildable
- **No stats yellows in any season** (stats feed 0/1,730), and the
  referee is named in **0/1,730 matches** (no X8 referee arm).
- The event feed carries cards, but the plain-Yellow target does not
  exist: **0 plain Yellow events in the whole corpus** (only
  YellowRed + Red events; event yellows per match 0.073–0.159 in
  dev). A cards target built on event yellows would be a
  YellowRed/Red count, not the yellow-cards market, and it breaks
  across eras (event yellows exist in dev but the plain-Yellow
  definition the market uses is absent everywhere).
- No arm, window, or line is therefore frozen for K-FI, nothing is
  fitted, and the virgin is not read for cards.

## Common
- No arm, window, or line is frozen for S/C/K/T-FI, nothing is
  fitted, and the virgin is not read for any of them. The frozen
  split (dev ≤ 2024, virgin 2025, 2026 untouched reserve) is NOT
  moved to manufacture a dev window: re-splitting after seeing the
  era break would be post-hoc window shopping. If future seasons
  add dev-era stats seasons, S/C/K/T-FI can be pre-registered
  fresh — they may not be rescued inside this prereg.

Verdicts: `reports/S_FI_VERDICT.md`, `reports/C_FI_VERDICT.md`,
`reports/K_FI_VERDICT.md`, `reports/T_FI_VERDICT.md`
(not-buildable).
