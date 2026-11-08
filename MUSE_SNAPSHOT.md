# Muse snapshot branch

This branch is a full replica snapshot of the production machine's state,
taken 2026-11-08 so the system can be reproduced on another machine.

## What this branch contains

- All production code from `main`, plus the work that previously lived
  only on the production machine: TipsterArea + FotMob fixture sources,
  the shots-on-target model (v5) and its halves split, the first cards
  model, the first-half corner model, the corner territorial multiplier,
  and the SofaScore SOT halves dataset adoption.
- The complete gathered datasets (about 3.2 GB), committed per group:
  - `data_enrichment/fotmob_full/` — full FotMob matchDetails responses,
    7,532 top-5 matches from 2022/23 onward (about 2.1 GB)
  - `data_enrichment/sot_backfill/` — raw FotMob responses used to fill
    the SOT halves gaps (about 816 MB), plus the curated label CSVs
  - `data_enrichment/` — SofaScore SOT halves dataset, combined halves
    dataset, shot/lineup features, cup actuals
  - `ta/` — TipsterArea fixtures, results, odds snapshots, raw scrapes
  - `raw/`, `xg_raw/` — football-data source files and xG dumps
  - Repository root — `all_matches*.csv`, `records_cache.jsonl`, current
    prediction and recommendation outputs
  - `archive/`, `ledger/`, `experiments/` data files

## Deliberately NOT included

- The local high-probability slip logic (probability floor 0.65 for all
  slip legs, slip ±5 and slip ±100 products). By the owner's decision
  (2026-11-01) that logic is local-only and is not pushed anywhere; this
  branch's slip recommender is the `main` version, with the 2026-11-03
  matchday anchoring for single/slip2 applied. The local commits are not
  deleted — they remain on the production machine.
- Secrets and machine-local runtime state: `.env`, `ta/session_cookies.json`,
  `.venv/`, `.cache/`, logs, and timestamped `*.bak-*` backups.

## Reproducing on a new machine

1. Clone this branch.
2. Create the virtualenv and install requirements
   (`python -m venv .venv && .venv/bin/pip install -r requirements.txt`).
3. Provide a `.env` with `API_FOOTBALL_KEY`.
4. Verification at snapshot time: 105 unit tests passed and
   `python test_core.py` reported all tests passed.
