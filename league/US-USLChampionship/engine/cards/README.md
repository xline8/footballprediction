# USL cards engine

Port of the US-MLS cards engine using unified stats-feed yellows
`yellow_home` and `yellow_away` (not event-feed card counts). Arms are Gate
Zero and X8, with missing or thin referee history falling back to Gate Zero.
Primary line is 4.5, ladder 3.5/4.5/5.5; warm-up is 2021 and scoring is
2022–2024.

Run dev with `python3 run_k_usl.py dev`. Virgin is not run in Stage 2 and is
coordinator-gated.
