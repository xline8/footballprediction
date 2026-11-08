# USL goals engine

Port of the US-MLS Dixon–Coles engine for `data/usl_matches.csv`. It reads
goals and uses the documented goals-only fallback because USL xG fields are
all `None`; the x3 arm is therefore not run. Dev arms are `gate_zero` and
`shr`, with warm-up 2021 and scored seasons 2022–2024. Outputs are
`results_dev.json` and `results_dev.csv`.

Run only the coordinator-approved dev command:

```sh
python3 run_g_usl.py dev
```

Virgin is not run in Stage 2; any virgin command is coordinator-gated.
