# S-VE engine

Virgin rerun: `python3 run_s_ve.py virgin`. It writes a deliberate refusal when DEV fails. S-VE failed both arms, so no 2026 Clausura row is loaded and no virgin predictions or fitted params are written. The potential count window is n=90, not 91, because match 1000018666 has `stats: None`. Frozen halves: 1H 0.4651, 2H 0.5349; the transitional season-end confirmatory read remains outstanding.

`run_s_ve.py` runs DEV on the 2025 Clausura seed and 2026 Apertura round blocks R1–7 and R8–13. It uses the joint ridge ratings and ratio/negative-binomial mechanics, with no xG fields. GZ uses the 200 ratio prior and RS the 20,000 prior. `results_dev.json` contains block and pooled line log-losses plus league-rate and trailing-10 baselines.
