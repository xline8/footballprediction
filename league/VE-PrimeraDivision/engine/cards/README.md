# K-VE engine

Virgin rerun: `python3 run_k_ve.py virgin`. It writes a deliberate refusal when DEV fails. K-VE failed DEV, so no 2026 Clausura row is loaded and no virgin predictions or fitted params are written. The potential count window is n=90, not 91, because match 1000018666 has `stats: None`. Frozen halves: 1H 0.3900, 2H 0.6100; the transitional season-end confirmatory read remains outstanding.

`run_k_ve.py` runs Gate Zero on stats yellows (`stats_yellow_home + stats_yellow_away`) at lines 5.5, 6.5, and 7.5. Missing yellow observations are omitted from updates and scoring; event-yellow columns are never read. DEV uses 2025 Clausura as seed and 2026 Apertura R1–7/R8–13 as scored blocks.
