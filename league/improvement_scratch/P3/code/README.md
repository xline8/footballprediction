# P3 Gate Zero — implementation

Reproduces the P3 variance-component Gate Zero test
(`../gate_zero_report.md`). Dev data only; nothing here reads a
sealed/virgin season, and nothing writes outside
`league/improvement_scratch/P3/`.

## Run

From the repo root (`~/workspace/footballprediction`):

```
.venv/bin/python league/improvement_scratch/P3/code/run_p3.py
```

Writes `../results.json`, `../results.csv`, `../details/<league>.json`.
Runtime ~10 s for all six leagues on this VM. Per-family runs:

```
.venv/bin/python league/improvement_scratch/P3/code/vc_goals.py MD-NationalDivision SG-PremierLeague J3 MX-ExpansionMX
.venv/bin/python league/improvement_scratch/P3/code/vc_sot.py LV-Virsliga SA-FirstDivision
```

## Files

- `vc_goals.py` — goals family. Loaders restricted to dev seasons;
  shipped-GZ replication through each league's own `dc.py`
  (J3: `g_j3.py`) and shipped fold protocols; `VCDC`, the
  Laplace-EM variance-component Dixon-Coles (tau_a, tau_d,
  sigma_era estimated per fold; rho grid, 270-day decay, MAXG=10
  matrix and scoring identical to shipped).
- `vc_sot.py` — SOT counting family. One re-implementation of the
  shipped v5-pattern engine (LV/SA template) with a mode switch:
  `gz` = asserted constants (ridge 100, K 8, ratio prior 200,
  NB r 79.94; validated to reproduce the shipped engine's dev LL
  exactly), `vc` = Laplace-EM ridge per refit, Gamma-Poisson MoM
  K, Beta-Binomial MoM ratio prior, MoM NB r — each estimated only
  from data available at that point of the walk.
- `run_p3.py` — driver: runs the six leagues sequentially, adds a
  final-walk component snapshot for the SOT leagues, applies the
  pre-registered verdict rule (improve in ≥5/6, none worse by
  >0.002) and writes the result artefacts.

Requires only numpy (project `.venv`). No commits were made; the
coordinator commits these artefacts.
