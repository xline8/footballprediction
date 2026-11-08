# G-ITB goals engine

Reads `league/IT-SerieB/data/itserieb_matches.csv`, keyed by FotMob
team id. Dev is 2021/2022 warm-up plus 2022/2023–2024/2025 scoring;
virgin is 2025/2026 only after the frozen preregistered gates. Run
`python3 league/IT-SerieB/engine/goals/run_g_itb.py dev` and then
`virgin-metrics` (or `virgin-predict --arm <arm>` for the shipped
arm's predictions). Prereg: `PREREG_G_ITB.md`; halves constant
0.4501. Observation is goals-only (xG era starts in the virgin).
X2 membership: frozen table `prereg/movers_itb.json`. Calibration
in results = actual − predicted.
