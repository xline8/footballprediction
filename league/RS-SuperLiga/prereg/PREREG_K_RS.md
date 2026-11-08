# Pre-registration — K-RS (RS-SuperLiga cards model): NOT BUILT

Frozen: 2026-11-10, before any fitting. Branch `wip-rs-superliga`.

K-RS is **not built**, by feasibility, recorded here so the absence is an
auditable decision and not an omission:

- There is no usable yellows target with the same meaning in dev and
  virgin. The dev-era event feed carries Card events at 0.041–0.120 per
  match (41–66 cards per season) against a real level of ~4.7 — the feed
  records essentially only YellowRed cards in 2021/2022–2024/2025
  (split-half trait reliability r = 0.060, `eda_summary.json:
  traits_dev.yellows_event_for`). The stats-feed `yellow_cards` key exists
  only in the virgin season (2025/2026, 4.230/match) and the reserve.
- The two candidate targets do not even agree where both exist: in the
  virgin season the stats feed undercounts the event feed by 0.432
  yellows/match (events 4.662 vs stats 4.230), exact agreement 72.6%, and
  the stats feed NEVER exceeds events (`eda_summary.json:
  cards_stats_vs_events`). Whichever feed were chosen, a dev gate would
  validate the arm on a different quantity than the one it would ship
  against.
- The X8 referee arm is dead independently: referee names are absent in
  all 1,192 dev matches (0 named; 197/296 named only in the virgin).
- No arm, window, or line is therefore frozen, nothing is fitted, and
  the virgin is not read for cards. If a future season adds a usable
  dev-era yellows feed, K-RS can be pre-registered fresh at that point —
  it may not be rescued inside this prereg.
