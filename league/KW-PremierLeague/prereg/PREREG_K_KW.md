# Pre-registration — K-KW (KW-PremierLeague cards): NOT BUILT

Frozen: 2026-11-10, before any fitting. Design authority:
`analysis/MODEL_DESIGN.md` (K-KW); evidence EDA F1/F2/F3/F5/F6.

K-KW is **not built**, by feasibility, recorded here so the absence
is an auditable decision and not an omission:

- No yellows target exists in ANY season at all: the stats feed
  carries no `yellow_cards` key in any of the 711 payloads (0
  matches with a stats feed anywhere), and the event feed carries
  ZERO plain Yellow events and ZERO YellowRed events in every
  season (0 in dev, 0 in the virgin, 0 in the reserve). The event
  feed records only straight Red cards (53 in the whole corpus).
  This is stronger than a definition break across eras: there is
  no yellows target to model in the first place. (CN precedent:
  plain Yellow events 0 in every season there too.)
- Referee coverage is 0% in every season, so no X8 referee arm
  exists either.
- Trait reliability is not measurable on dev (no target), and no
  1H share is computable (no yellows events with times in dev —
  the event feed itself only exists in dev in 2024/2025), so no
  line can be selected and no halves constant frozen.
- No arm, window, or line is therefore frozen, nothing is fitted,
  and the virgin is not read for cards. The frozen split
  (dev ≤ 2024/2025, virgin 2025/2026, 2026/2027 untouched reserve)
  is NOT moved to manufacture a dev window. If future seasons add
  a yellows target, K-KW can be pre-registered fresh — it may not
  be rescued inside this prereg.

Verdict: `reports/K_KW_VERDICT.md` (not-buildable).
