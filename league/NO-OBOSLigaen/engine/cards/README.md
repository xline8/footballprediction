# K-NO-OBOS cards engine

Seeded from the NO-Eliteserien cards engine (production model_cards
pattern via J1). Reads `../../data/no_obos_matches.csv`. Target is
event-unified yellows (`yellow_home + yellow_away`) — the stats feed
carries no yellow_cards key in this league (prereg). Development:
2021 warm-up, 2022–2025 scored, per-match predict-then-update. Arms
are `gate_zero` and `x8` (referee covariate, F8 r=0.715; fixtures
without a named referee fall back to Gate Zero). Primary line is 3.5.
Presentation-only 1H share is 0.306 (event times).

Run from this directory: `python3 run_k_obos.py dev` → `results_dev.json`
/ `results_dev.csv`. Virgin subcommands exist but the candidate failed
its dev gate (Gate Zero), so the virgin was deliberately NOT read.
