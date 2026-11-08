# J3 analysis — pointer

The J.League exploration (steps 1–6 of the per-league process) was run
once for the whole J.League system; its documents live in
`league/J1/analysis/` and cover J3 explicitly throughout:

- `DATA_UNDERSTANDING.md` — coverage matrix per tier (J3: scores-only
  outside a 62-match 2025 window; HT missing for 6.8% of matches)
- `PREPROCESSING.md` — derivation rules for `league/J3/data/` CSVs
- `EDA.md` — findings F1–F14 with per-tier verdicts (J3 traits in F2,
  cross-tier bridge F4, feasibility F13: goals model only)
- `FEATURES.md` — X1–X9 accepted / R1–R13 rejected, per-tier availability
- `MODEL_DESIGN.md` — candidate G-J3 (§2) is J3's only design

J3-specific artefacts produced later (preregs, verdicts) live in this
league's own `league/J3/` tree (`prereg/`, `reports/`).
