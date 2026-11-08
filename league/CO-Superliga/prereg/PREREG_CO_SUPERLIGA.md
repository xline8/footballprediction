# Pre-registration — CO-Superliga (FotMob 11536)

**Committed before any fitting. No fitting is done under this prereg.**

## Feasibility verdict (the preregistered question)

Is there enough data for a season-blocked walk-forward dev + a virgin
window at all? **No — for every candidate.** This prereg records the
NOT BUILDABLE verdict with its payload-level evidence, so that no
fitting, no virgin read, and no post-hoc arm can follow from it.

## Evidence (payload-verified 2026-11-10, 12/12 payloads read)

- 12 matches total, exactly 2 per season, seasons 2021–2026. One
  two-legged Final tie per year (champion vs champion); no other rounds.
- Scores 12/12; `content.stats` 7/12 (2023 ×2, 2024 leg 1, 2025 ×2,
  2026 ×2); shotmap with shots > 0 in 4/12 (2025–26 only, 114 shots);
  referee field 0/12; `yellow_cards` stats-block zero-filled [0, 0] in
  all three 2023/2024 stats matches.
- 9 distinct clubs; no club plays more than 2 matches in any season;
  each season's two teams arrive with zero prior in-competition matches
  that season.

## Gate arithmetic (why no window exists)

- Dev = season-blocked walk-forward: a "season" is 2 matches between 2
  teams. Dixon-Coles / Poisson / NB ratings are not estimable — every
  season's teams have zero prior Superliga matches, and the most
  frequent clubs hold 4 matches in 6 years.
- Virgin = 2026, n=2. Calibration SE at OU 2.5 ≈ 33pp (base rate 4/12),
  ≈35pp at p=0.5 — ~33× the 1pp clean-PASS threshold. One goal flips
  any verdict by 50pp. A PASS/FAIL at n=2 would be a coin flip.
- Pooled n=12 does not rescue it: OU 2.5 SE ≈ 13.6pp, still 13× the
  clean threshold.

## Registered decisions

- Arms: **none** (no candidate reaches design).
- Primary lines: **none chosen**.
- Virgin window (2026): **NOT READ** for any candidate — deliberately
  unread, because no arm passes (or can pass) a dev gate. Reading it
  would be a result in search of a gate.
- Format rule (frozen for the record): two-legged Final, aggregate
  winner; level on aggregate → straight to penalties (2025: 1–1 agg,
  Pen 3–4; no extra-time halves in any payload). No away-goals decider
  observed.
- Halves constants: **none frozen** (1H shares at n=7–29 are noise).
- Features X1–X9: **all DROPPED** (see `analysis/FEATURES.md`).
- What ships: **nothing** — no engine, no fitted params, no predictions.

## Verdict

**0 PASS / 0 FAIL / 5 NOT BUILDABLE.** G-COS, S-COS, C-COS, K-COS,
T-COS are all NOT BUILDABLE on thinness. The league is complete on
this verdict. Any future revisit (e.g. a pooled cross-super-cup
transfer design) needs a new preregistration outside this program's
per-league gates; nothing is scheduled — at 2 matches/year the
competition will not reach a gateable sample.
