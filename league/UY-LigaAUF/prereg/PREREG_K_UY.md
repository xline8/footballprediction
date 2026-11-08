# Pre-registration — K-UY (UY-LigaAUF cards): NOT BUILT

Frozen: 2026-11-10, before any fitting. Design authority:
`analysis/MODEL_DESIGN.md` (K-UY); evidence EDA F1/F3/F6,
FEATURES.md X8.

K-UY is **not built**, by feasibility, recorded here so the absence
is an auditable decision and not an omission:

- There is no consistent cards target in any dev season under
  EITHER source. Stats-feed yellows are absent in every season
  (0/1,717 matches with a stats feed; no `yellow_cards` /
  `red_cards` key in any raw JSON). The event-feed fallback target
  is not consistent across dev: plain Yellow Card events exist ONLY
  from 2023 onward (2021: Yellow 0, YellowRed 44, Red 40; 2022:
  Yellow 0, YellowRed 63, Red 63; 2023: Yellow 1,659; 2024: Yellow
  1,597). A yellows target defined on the event feed would have no
  dev window in 2021–2022 (warm-up + first scored season) and a
  two-season window in 2023–2024 — a target-definition break, not a
  modelling window (the NO-2Divisjon precedent, where Yellows
  existed only from 2024).
- Trait reliability is not measurable on a consistent dev target
  (split-half r null, n = 0 teams), no 1H yellows share is
  computable on dev as a frozen constant (0 matches with period
  splits in dev; event-time 1H yellows are not derived — the dev
  card events before 2023 are YellowRed/Red only, the wrong
  target), and the X8 referee covariate cannot be measured on dev
  (no referee field populated in any dev match; named in 0/1,717
  matches, every season). No line can be selected.
- No arm, window, or line is therefore frozen, nothing is fitted,
  and the virgin is not read for cards. The frozen split is NOT
  moved to manufacture a dev window. If future seasons add a dev
  cards target, K-UY can be pre-registered fresh — it may not be
  rescued inside this prereg.

Verdict: `reports/K_UY_VERDICT.md` (not-buildable).
