# Pre-registration — K-SE (SE-Ettan cards): NOT BUILT

Frozen: 2026-11-10 WIB, before any fitting. Design authority:
`analysis/MODEL_DESIGN.md` (K-SE); evidence EDA F1/F2/F3/F5/F6,
FEATURES.md X5/X8.

K-SE is **not built**, by feasibility, recorded here so the absence
is an auditable decision and not an omission:

- The canonical cards target (stats-feed yellows) exists in NO
  season: the stats feed is 0% in 2021–2025 (0 matches with a stats
  feed in any season; stats keys per season are empty in
  `eda_summary.json`). The stats era never starts. There is no dev
  season, no warm-up season, and no scored dev window at all under
  the canonical target definition.
- The event feed DOES carry card events, and that evidence is
  preserved here in full (EDA F5) so a future program-level decision
  can be made on it: 4,745 plain Yellow events, 98 YellowRed and 113
  Red in 2021–2024; event yellows 3.4375 / 3.2813 / 3.3708 per match
  in 2022–2024; event-yellows team trait split-half r 0.549 (n = 49
  teams, 2022–2024); event-time 1H yellows share 0.2841 (1,375 of
  4,840 event yellows, 2022–2024; per-season 0.3000 / 0.2781 /
  0.2737). That is materially better evidence than QA had (zero plain
  Yellows in dev). K-SE is still not-buildable under the frozen split,
  for three independent reasons, any one of which suffices:
  (a) there is no stats feed anywhere, so the canonical cards target
  does not exist and the event-derived series cannot be validated
  against any official count — in QA the event feed was shown to
  undercount structurally when the two feeds coexisted, and SE has
  no coexistence window to check; (b) the dev era has no complete
  window from one consistent source — 2021 (the warm-up season) has
  zero events, so an event-yellows model would have no target at all
  in its first dev season; (c) X8 is impossible — referee coverage is
  0% in every season (0 distinct referees in the raw scan), so no
  referee arm exists.
- Revisiting K would need a program-level decision from Jarvis to
  (i) adopt event-derived yellows as the target by definition and
  (ii) re-split dev to start in 2022. That decision is NOT made here,
  and no K engine is built in this league without it.
- No arm, window, or line is therefore frozen, nothing is fitted,
  and the virgin is not read for cards. The frozen split
  (dev ≤ 2024, virgin 2025, 2026 untouched reserve) is NOT moved to
  manufacture a dev window: re-splitting after seeing the era break
  would be post-hoc window shopping.

Verdict: `reports/K_SE_VERDICT.md` (not-buildable).
