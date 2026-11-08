# Phase 2 — Preprocessing: IE-PremierDivision

Run from the repository root:

`/home/hatch/workspace/footballprediction/.venv/bin/python league/IE-PremierDivision/data/build_data.py`

This creates `data/ie_matches.csv` and `data/ie_team_matches.csv`. The
builder keeps finished index rows, asserts match-id uniqueness, flattens All,
FirstHalf and SecondHalf stats where present, and excludes penalty-shootout
shots from shotmap aggregates.

Cards are intentionally different from the SCO source rule. `yellow_home`
and `yellow_away` equal event Yellow plus YellowRed; `cards_source` is
`events` when the payload contains events and `none` otherwise. Stats-feed
yellow counts remain in their original columns for the exact-agreement audit.
Team-match `yellow_cards_for/against` uses the same event target.

The phase rule is fixed to `regular`, after verifying the round inventory.
No model, fitted parameter, or 2026 target statistic is produced here.
