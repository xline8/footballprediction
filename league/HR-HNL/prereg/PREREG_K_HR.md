# Pre-registration — K-HR (HR-HNL cards model): NOT BUILT

Frozen: 2026-11-10, before any fitting. Branch `build/hr-hnl`.

K-HR is **not built**, by feasibility, recorded here so the absence is an
auditable decision and not an omission. The stats-vs-events artefact
check was run FIRST (EDA F6), before any target freeze, as the programme
requires:

- The stats feed publishes `yellow_cards`/`red_cards` keys in EVERY
  season — but the early-era series (2021/2022–2022/2023) is not the
  same quantity as the rich-era one: mean 2.767 / 2.517 yellows per
  match with **37.8% of matches at zero total yellows in both seasons**,
  at a stable fouls level (24.3 / 24.2 per match) that matches the rich
  era (25.4–26.6). The rich era (2023/2024+) reads 4.144 / 4.250 /
  3.961 with a zero-share of 1.1–5.0%. The early-era 1H share in the
  51 split matches of 2022/2023 is 0.145 vs ≈ 0.327 in the rich era.
- The event feed cannot supply the early era either: before 2023/2024
  it carries NO yellow-card events at all (only Red/YellowRed; mean
  event "yellows" 0.128/match in both early seasons).
- Where both sources exist (2023/2024+), they agree well — exact
  83.3% / 78.3% / 85.0%, mean stats − events −0.217 / −0.278 / −0.133 —
  so the rich-era quantity is coherent; the break is at the boundary,
  the TH/ZA-class era artefact.
- The conveyor feasibility rule requires the target to exist AND a
  valid virgin window to contain it, validated by the programme's
  season-blocked walk-forward (warm-up + ≥3 scored dev seasons). The
  credible (rich-era) target exists in exactly two dev-era seasons
  (2023/2024, 2024/2025) before the 2025/2026 virgin: at best warm-up
  2023/2024 + ONE scored season. Pooling the defective early-era rows
  would gate the arm on a different target than the one it ships
  against (the T-FI reasoning, verbatim in structure).
- X8 (referee) is independently dead in this league: split-half
  strictness r = 0.239 (EDA F7), despite adequate name coverage.

No arm, window, or line is therefore frozen, nothing is fitted, and
the virgin is not read for cards. If a future season adds rich-era dev
depth (e.g. a fresh build with virgin 2026/2027 and scored dev
2023/2024–2025/2026), K-HR can be pre-registered fresh at that point —
it may not be rescued inside this prereg.
