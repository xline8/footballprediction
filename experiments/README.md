# Experiments

One-off research scripts live in this directory. They are not part of the
daily pipeline, and no production module imports them.

Run a script from the repository root:

```bash
python experiments/experiment_xg_dc.py
```

Each script adds the repository root to `sys.path` before it imports
production modules, and it reads and writes data files at the root. The
results that matter are written up in [docs](../docs/).

## Note on Pinnacle column names (2026-10-29)

football-data.co.uk renamed the Pinnacle columns in its 2026/27 files:
opening `PSH/PSD/PSA` became `PPH/PPD/PPA`, and closing `PSCH/PSCD/PSCA`
became `PPCH/PPCD/PPCA`. Production code reads the new names first and
falls back to the old ones for earlier seasons. These experiment
scripts predate the rename and still read the `PS*` names, so on
2026/27 data their Pinnacle inputs come back empty. They are kept
as-run on purpose: their historical outputs were produced with the
column names of their time, and editing them now would break the
reproducibility of those results. Copy a script out of this directory
and update the column names there if you need to rerun one against
current-season data.
