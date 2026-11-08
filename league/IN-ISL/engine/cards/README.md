# K-IN cards engine

Production model_cards.py pattern, ported from the AU-ALeague engine. Target is EVENT-UNIFIED yellows (`yellow_home + yellow_away` in `league/IN-ISL/data/in_matches.csv`, built from the event feed per the pre-fitting decision in analysis/DATA_UNDERSTANDING.md §3). Gate-Zero-only: the X8 referee arm is not built because IN referee coverage is 13.5% in dev and 0% in the virgin, with no computable strictness trait. Primary line 4.5, ladder 3.5/4.5/5.5; halves presentation via frozen constant 0.366.

```text
.venv/bin/python league/IN-ISL/engine/cards/run_k_in.py dev
.venv/bin/python league/IN-ISL/engine/cards/run_k_in.py virgin --arms gate_zero   # refuses non-passing arms
```

Verdict: FAIL at dev (naive trailing-10 won) — virgin not read; see `reports/K_IN_VERDICT.md`.
