# Verdict — K-HR (HR-HNL cards): **NOT BUILT (target artefact)**

Frozen decision: PREREG_K_HR.md (e9872c4, before any fitting).

No model was fitted and the virgin was not read for cards. The
stats-vs-events artefact check (EDA F6, run before any target freeze)
showed an era-flipped measurement break at the 2023/2024 boundary in
BOTH sources:

- Stats `yellow_cards` exists in every season, but the early-era
  (2021/2022–2022/2023) series is defective: mean 2.767 / 2.517 per
  match, 37.8% of matches with zero total yellows in both seasons, at
  a stable fouls level (24.3 / 24.2 per match) equal to the rich era's
  (25.4–26.6); early-era 1H yellow share in the 2022/2023 split
  subset is 0.145 vs ≈ 0.327 rich-era.
- The event feed carries NO yellow-card events before 2023/2024
  (mean event "yellows" 0.128/match = red cards only), so no
  event-derived target covers the early era either.
- Rich era (2023/2024+) is coherent: stats-vs-events exact agreement
  83.3% / 78.3% / 85.0%, mean stats − events −0.217 / −0.278 / −0.133.

A credible target therefore spans at most warm-up 2023/2024 + one
scored dev season (2024/2025) before the 2025/2026 virgin — below the
programme's season-blocked walk-forward minimum (warm-up + ≥3 scored
seasons). Pooling the defective era would gate an arm on a different
quantity than it ships against (T-FI precedent). X8 (referee) is
independently dead in this league (split-half strictness r = 0.239,
EDA F7).

Revisit condition (recorded in PREREG_K_HR): a fresh pre-registration
once rich-era depth suffices — e.g. virgin 2026/2027 with scored dev
2023/2024–2025/2026. Not rescuable inside this prereg.
