# C-TR corners engine

Run from the repository root with the project interpreter:

```bash
~/workspace/footballprediction/.venv/bin/python league/TR-SuperLig/engine/corners/run_c_tr.py dev
~/workspace/footballprediction/.venv/bin/python league/TR-SuperLig/engine/corners/run_c_tr.py virgin --arms gate_zero x7
```

`dev` filters at load time to seasons 2021–2025 and writes the dev result
files. The virgin command must be given only arms that pass the persisted dev
gate; it then reads 2025/2026 and writes the virgin results, fitted parameters,
and the predictions CSV. The harness uses date-grouped state so same-date
matches cannot see one another.

Ambiguity resolutions: the prereg's “league per-team mean” fallback is the
decay-weighted `(bh + ba) / 2` for both corner-for and corner-against; the
naive team means otherwise use the last ten prior matches. Territorial
history retains all prior matches and counts only complete covariate entries
as valid within the last ten, matching the min-8 contract. The CSV beta field
is a compact JSON list for both arms, and half probabilities use each half's
own mean with the full-time fitted `r`, as specified.
