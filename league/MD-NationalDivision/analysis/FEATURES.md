# Step 5 — Feature Engineering: MD-NationalDivision

## Adopted

- **X1 goals-only (fallback)**: the X1 xG blend has no xG to
  blend — no `expected_goals*` key exists in any of the 556
  payloads and there is no shotmap. The observation is goals-only
  in every match, the blend's documented fallback (FI precedent).
  Justified by trait reliability: split-half r GF 0.885 / GA 0.877
  (dev era) — goals themselves are a reliable trait here.
- **X2 entrant offset: KEPT** (EDA F4). 3 dev transitions, mean
  GF diff −0.363 (3/3 negative), GA diff +0.780 (2/3 positive);
  clamped offsets g_log −0.223 / c_log +0.223. The rule (recompute
  from completed transitions before each predicted season, <3
  completed → offset 0, multipliers clamped [0.8, 1.25]) is what is
  frozen, not the realised numbers. Expected numerically inert on
  the dev scored window (see EDA F4); active only where the rule
  fires.
- **SHRINK**: program-standard G arm (n<6 prior in-league matches
  ⇒ attack/defence exponents scaled by n/6 at prediction).
  Expected inert under season-blocked prediction here too (any
  team in a prior season has ≥14 prior matches; unrated teams sit
  at league mean 0.0). Run and reported anyway.

## Dropped (with reason — every one is a data absence, not a modelling choice)

- **X3 set-play share** — no stats feed in any season (0/556).
- **X4 on-target ratio** — no stats feed, no shotmap (0/556).
- **X6 shot volume** — no total-shots target in any season.
- **X7 box touches / territory (corners)** — no corners target,
  no `touches_opp_box` in any season.
- **X8 referee (cards)** — referee named in 0/556 matches, all
  seasons; additionally no yellows target exists at all (zero
  plain Yellow events corpus-wide).
- **X9 keeper saves** — no stats feed in any season.

## Frozen halves constants (dev era only)

- goals 1H share: **0.4388** (1,005 goals, 336 matches with
  events, dev era 2021/2022–2024/2025, awarded excluded).
- SOT / corners / total shots / yellows: **none** — no period
  splits exist in any season and there are no count markets.
  Halves presentation for goals uses the frozen constant only.
