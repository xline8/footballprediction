# Verdict — K-SE (SE-Ettan cards): **NOT-BUILDABLE**

Frozen decision: PREREG_K_SE.md (prereg commit
2fc8d51c13736643f6156b1c71abb11e21b7de08, before any fitting).

No model was fitted, no dev gate was run, and the virgin was not
read for cards. Reason: the canonical cards target (stats-feed
yellows) exists in NO season — the stats feed is 0% in 2021–2025
(0 matches with a stats feed in any season; stats keys per season
are empty in `eda_summary.json`). The stats era never starts. There
is no dev season, no warm-up season, and no scored dev window at all
under the canonical target definition.

The event feed DOES carry card events, and that evidence is preserved
here in full (EDA F5) so a future program-level decision can be made
on it — this is the one judgement call in the SE EDA, and the
evidence is materially better than QA had (QA's dev event feed
carried zero plain Yellow events):

- Event card totals, dev era 2022–2024: 4,745 plain Yellow events,
  98 YellowRed, 113 Red (2021–2024 totals; 2021 itself has zero
  events of any kind).
- Event yellows per match: 3.4375 in 2022, 3.2813 in 2023, 3.3708 in
  2024 (mean 3.28–3.44/match).
- Event-yellows team trait split-half r 0.549 (n = 49 teams,
  2022–2024) — a moderately reliable team trait, descriptive only.
- Event-time 1H yellows share 0.2841 (1,375 of 4,840 event yellows,
  2022–2024; per season 0.3000 / 0.2781 / 0.2737) — descriptive only,
  NOT a frozen halves constant (no period splits exist to validate
  it against).

K-SE is still not-buildable under the frozen split, for three
independent reasons, any one of which suffices: (a) there is no
stats feed anywhere, so the canonical cards target does not exist
and the event-derived series cannot be validated against any
official count — in QA the event feed was shown to undercount
structurally when the two feeds coexisted, and SE has no
coexistence window to check; (b) the dev era has no complete window
from one consistent source — 2021 (the warm-up season) has zero
events, so an event-yellows model would have no target at all in its
first dev season; (c) X8 is impossible — referee coverage is 0% in
every season (0 distinct referees in the raw scan), so no referee
arm exists.

**Flag for Jarvis (program-level decision, NOT a blocker):**
revisiting K would need a decision from Jarvis to (i) adopt
event-derived yellows as the target by definition and (ii) re-split
dev to start in 2022. That decision is NOT made here, and no K
engine is built in this league without it. This is a feasibility
verdict recorded pre-fitting, not a gate FAIL. The frozen split was
not moved to manufacture a dev window. K-SE may be pre-registered
fresh once that decision is made; it may not be rescued inside this
prereg.
