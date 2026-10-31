# Native xG experiment

This branch implements an opt-in source selector for the Dixon–Coles xG
inputs and persists xG provenance/missingness in feature rows.

Environment variables:

- `FOOTBALL_XG_SOURCE=understat` (default, existing behavior)
- `FOOTBALL_XG_SOURCE=native` (football-data `HxG/AxG` only)
- `FOOTBALL_XG_SOURCE=native_priority` (native first, Understat fallback)
- `FOOTBALL_T3_FEATURES=base` (default)
- `FOOTBALL_T3_FEATURES=xg_aware` (adds rolling xG missingness flags)

Run the reproducible comparison with:

```text
python experiments/experiment_native_xg.py
```

The experiment uses monthly expanding-window evaluation on the current
`2026/27` tail. It does not write model state, prediction CSVs, or production
configuration.

Observed result on the checked-out data:

| Variant | DC log loss | DC Brier | T3 log loss | T3 Brier |
|---|---:|---:|---:|---:|
| Understat + base | 0.97557 | 0.57836 | 1.01683 | 0.60889 |
| Native-priority + base | **0.97464** | **0.57777** | **1.01674** | **0.60882** |
| Understat + xG-aware | — | — | 1.01724 | 0.60918 |
| Native-priority + xG-aware | — | — | 1.01713 | 0.60910 |

Native-priority is a small improvement on this current-season sample, while
the missingness flags slightly worsen proper scoring. The default remains the
existing Understat/base configuration until a larger out-of-sample sample is
available.
