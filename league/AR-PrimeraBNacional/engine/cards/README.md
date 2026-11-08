# K-BNAC cards engine

Run `python3 run_k_bnac.py --dev` for the frozen 2023–2025 walk-forward, or `python3 run_k_bnac.py --virgin` for the single 2023–2026 chronological pass. The virgin command asserts zero 2021–2022 rows, 648 2026 rows, and exact reproduction of the frozen dev pooled LLs before writing outputs.

The virgin pass continues the same `Online` state through 2026. `fitted_params_virgin.json` contains the `cutoff_state` at the end of the 2026 window: decayed league means and each team's four shrunk venue-split attack/defence rates. It is a state snapshot, not a refit on the virgin outcomes. The shipped prediction CSV uses the selected arm only; referee appointments missing before kickoff must operationally fall back to Gate Zero. Half means are presentation-only, split with the frozen 0.390091 / 0.609909 constants.
