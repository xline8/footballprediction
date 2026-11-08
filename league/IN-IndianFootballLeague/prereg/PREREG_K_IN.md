# Pre-registration — K-IN (IN-IndianFootballLeague cards): NOT BUILT

Frozen: 2026-11-10, before any fitting. Design authority:
`analysis/MODEL_DESIGN.md` (K-IN); evidence EDA F1/F2/F3/F5/F6.

K-IN is **not built**, by feasibility, recorded here so the absence
is an auditable decision and not an omission:

- No consistent yellows target exists in dev under either source:
  the stats feed carries no `yellow_cards` key in any season
  (0/608 matches with a stats feed), and the event feed carries
  **zero plain Yellow events in every dev season AND in the
  virgin** (2021/2022–2025/2026: YellowRed + Red only; YellowRed
  totals 12 / 13 / 16 / 7 / 0). Plain Yellow events appear ONLY in
  the untouched reserve (27 in 2026/2027) — a target-definition
  break that sits entirely outside the modelled eras (BY
  precedent, stronger form: there the absence was total; here it
  is total in dev + virgin). Event-derived "yellows" in dev are
  YellowRed counts of 0.06–0.11/match — not a cards target.
- Referee coverage cannot rescue it: referees ARE named in dev
  (453/496, 91.3%) — the X8 input exists in dev — but coverage
  collapses in the virgin (4/66, 6.1%), so no referee arm could
  be evaluated or shipped on the virgin; and with no yellows
  target there is nothing for a referee arm to predict.
- Trait reliability is not measurable on dev for any yellows
  target (split-half r null, n = 0 teams with a target), and no
  1H share is computable (0 matches with period splits; the
  event-yellows 1H share 0.0625 on 48 YellowRed events is not a
  cards constant), so no line can be selected and no halves
  constant frozen.
- No arm, window, or line is therefore frozen, nothing is fitted,
  and the virgin is not read for cards. The frozen split
  (dev ≤ 2024/2025, virgin 2025/2026, 2026/2027 untouched reserve)
  is NOT moved to manufacture a dev window. If future seasons add
  a consistent yellows target in dev, K-IN can be pre-registered
  fresh — it may not be rescued inside this prereg.

Verdict: `reports/K_IN_VERDICT.md` (not-buildable).
