# S-IE shots-on-target engine
Reads `data/ie_matches.csv`, target `ShotsOnTarget_home + ShotsOnTarget_away` (stats feed). Warm-up 2022, scores 2023–2025 at lines 6.5/7.5/8.5 (primary 7.5). Arms GZ, RS (BB prior 200→20000); X4/X6 not built (shotmap era 2025+ only, ERA-INSUFFICIENT). Virgin 2026 conditional on the dev gate — NOT read in this build (dev gate failed). Prereg: `prereg/PREREG_S_IE.md` (halves constant 0.4491).
Run: `python3 league/IE-PremierDivision/engine/sot/run_s_ie.py dev`.
Outputs: `results_dev.json/csv`.
