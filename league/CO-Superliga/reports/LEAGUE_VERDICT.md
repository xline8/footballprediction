# League verdict — CO-Superliga (FotMob 11536) — **0 PASS / 0 FAIL / 5 NOT BUILDABLE**

## What it is

The Colombia Superliga is an annual two-legged Final (champion vs
champion), not a league: 12 matches total, exactly 2 per season,
2021–2026, 9 distinct clubs, no club playing more than 2 matches in a
season. Format frozen from payloads: aggregate winner; level on
aggregate → straight to penalties (2025: 1–1 agg, Pen 3–4; no extra
time in any payload); no away-goals decider observed.

## Verdict table

| Candidate | Dev | Virgin | Verdict |
|-----------|-----|--------|---------|
| G-COS goals | No window (2/season) | **Not read** (n=2) | **NOT BUILDABLE** |
| S-COS SOT | No window (stats 7/12) | **Not read** | **NOT BUILDABLE** |
| C-COS corners | No window (stats 7/12) | **Not read** | **NOT BUILDABLE** |
| K-COS cards | No window; no referee 0/12 | **Not read** | **NOT BUILDABLE** |
| T-COS total shots | No window (stats 7/12) | **Not read** | **NOT BUILDABLE** |

No arm passed or failed a gate, because no gate could be run: the
virgin (2026, n=2) has a calibration SE of ≈33–35pp against a 1pp
clean-PASS threshold, and pooled n=12 still gives ≈13.6pp. A verdict
there would be decided by a single goal. Nothing was fitted, no engine
was built, no predictions were issued, no halves constants were frozen
(X1–X9 all dropped — see `analysis/FEATURES.md`).

## Payload-level data-quality notes

- Index `has_shotmap=True` (2025/2026) is key presence only;
  `shotmap.shots` is empty in 8/12 payloads. Real shotmap: 4 matches.
- Stats-block `yellow_cards` is zero-filled [0, 0] in the three
  2023/2024 stats matches (9/10/5 Card events in the same matches).
- 2024 leg 2 has no stats block while its pair does (leg-asymmetric
  coverage).

## Note on the parent league

The only conceivable model would borrow Primera A ratings (warehouse
league_id **274** — the brief's "FotMob 113" does not match the
warehouse; Primera A's own config records `fotmob_id: 274`, 3 PASS /
2 FAIL). That transfer cannot be validated in-competition (no dev, no
virgin), so it is rejected for this program and not built. A pooled
cross-super-cup design would need a fresh preregistration outside the
per-league gates; none is scheduled — at 2 matches/year this
competition will not reach a gateable sample.

## League complete

**CO-Superliga is complete: 0 PASS / 0 FAIL / 5 NOT BUILDABLE.**
Nothing joins the daily pipeline. `league/PROGRAM_STATUS.md` not
touched (coordinator owns it).
