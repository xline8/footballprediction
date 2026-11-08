# T-QASD engine

Implements arms A (v1), B (v2 level), and C (E9 trailing-r) for total
shots. It loads the 38-row 2024/2025 stats history, warms on rounds 1–7,
scores rounds 8–14, and groups state updates by date. Run
`python3 run_t_qasd.py dev`; virgin execution requires a separate explicit
flag in the final runner and is never part of the default dev run.
