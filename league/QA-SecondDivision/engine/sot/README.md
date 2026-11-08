# S-QASD engine

Reads `data/qasd_matches.csv`, uses stats SOT totals, and scores only
2025/2026 rounds 8–14. The 28-match warm-up and 2024/2025 38-row stats
history are loaded before scoring. State is predict-then-update by date;
same-date matches never see one another. `dev` is the default safe run:

```sh
python3 run_s_qasd.py dev
QASD_RUN_VIRGIN=1 python3 run_s_qasd.py virgin
```

The virgin command is intentionally refused without the explicit flag.
