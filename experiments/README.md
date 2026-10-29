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
