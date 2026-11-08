# USL total-shots engine

Port of the IT-SerieB A/B/C shots-family engine using USL stats-feed total
shots. `M_BAR` is frozen at 24.4 and the primary line is 24.5, with ladder
23.5/24.5/25.5. Season 2021 is warm-up, 2022 is tuning only, and the dev
gate pool is 2023–2024. Tuning outcomes are written to `fitted_params.json`
and included in `results_dev.json`.

Run dev with `python3 run_t_usl.py dev`. Virgin is not run in Stage 2 and is
coordinator-gated.
