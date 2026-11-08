# K-IE cards engine
Reads the EVENT-UNIFIED target `yellow_home/yellow_away` (Card events Yellow+YellowRed, `cards_source='events'`) from `data/ie_matches.csv` — the stats-feed yellows are an artefact source in this league and are never the target. Seed 2021, scores 2022–2025 at lines 3.5/4.5/5.5 (primary 4.5). Gate Zero ONLY — X8 referee arm dropped in FEATURES (reliability r = 0.239; named-referee coverage 0% in 2021). Virgin 2026 conditional on the dev gate — NOT read in this build (dev gate failed). Prereg: `prereg/PREREG_K_IE.md` (halves constant 0.3238).
Run: `python3 league/IE-PremierDivision/engine/cards/run_k_ie.py dev`.
Outputs: `results_dev.json`.
