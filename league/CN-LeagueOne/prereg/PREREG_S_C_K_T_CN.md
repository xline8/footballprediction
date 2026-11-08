# Pre-registration — S/C/K/T-CN (CN-LeagueOne SOT / corners / cards / total shots): NOT BUILT

Frozen: 2026-11-10, before any fitting. Design authority:
`analysis/MODEL_DESIGN.md` (S/C/K/T-CN); evidence EDA F1/F2/F3/F5/F6,
FEATURES.md. Split decision: the brief's suggested split, frozen
here — dev ≤ 2024, virgin 2025, 2026 reserve; the split is NOT
moved to manufacture a dev window for any of these candidates.

S-CN, C-CN, K-CN and T-CN are **not built**, by feasibility, recorded
here so the absence is an auditable decision and not an omission.
The virgin is not read for any of them.

## S-CN (shots on target) — not-buildable
- The SOT target exists ONLY where a stats feed exists: **0
  matches with a stats feed in every season 2021–2026 (0/1,572)**.
  No SOT column is populated in any season; shotmap 0/1,572.
- There is no dev season, no warm-up season and no scored dev
  window at all; trait reliability is not measurable on dev
  (split-half r null, n = 0 teams); no 1H share is computable on
  dev (0 matches with FirstHalf/SecondHalf splits in dev), so no
  line can be selected and no halves constant frozen.

## C-CN (corners) — not-buildable
- The corners target exists ONLY where a stats feed exists: **0
  matches with a stats feed in every season 2021–2026 (0/1,572)**.
- Same consequence as S-CN: no dev window, no trait, no line, no
  halves constant. The X7 opp-box-touches covariate is likewise
  absent in dev, so no touches variant has a dev window either.

## T-CN (total shots) — not-buildable
- The total-shots target exists ONLY where a stats feed or shotmap
  exists: **stats 0/1,572, shotmap 0/1,572 in every season**.
- Same consequence as S-CN/C-CN: no dev window, no trait, no line,
  no halves constant.

## K-CN (cards) — not-buildable
- **No stats yellows in any season** (stats feed 0/1,572), and the
  referee is named in **0/1,572 matches** (no X8 referee arm).
- The event feed carries cards, but the plain-Yellow target does not
  exist in any season: **0 plain Yellow events in the whole corpus
  (0 in 1,572 matches)** — only YellowRed (5/21/25/14 in dev) and
  Red (55/51/46/41 in dev) events. A cards target built on event
  yellows would be a YellowRed/Red count, not the yellow-cards
  market, and the plain-Yellow definition the market uses is absent
  everywhere. This is the strongest K not-buildable case in the
  program: not a target-definition break across eras, but a target
  that never exists.
- No arm, window, or line is therefore frozen for K-CN, nothing is
  fitted, and the virgin is not read for cards.

## Common
- No arm, window, or line is frozen for S/C/K/T-CN, nothing is
  fitted, and the virgin is not read for any of them. The frozen
  split (dev ≤ 2024, virgin 2025, 2026 untouched reserve) is NOT
  moved to manufacture a dev window: re-splitting after seeing the
  era break would be post-hoc window shopping. If future seasons
  add dev-era stats seasons, S/C/K/T-CN can be pre-registered
  fresh — they may not be rescued inside this prereg.

Verdicts: `reports/S_CN_VERDICT.md`, `reports/C_CN_VERDICT.md`,
`reports/K_CN_VERDICT.md`, `reports/T_CN_VERDICT.md`
(not-buildable).
