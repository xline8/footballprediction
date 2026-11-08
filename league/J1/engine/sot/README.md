# S-J1 shots-on-target engine

This is the league-local implementation of the frozen S-J1 preregistration. It uses the v5 decayed ratings, Newton ridge regression, trailing-10 naive tracker, negative-binomial line probabilities, and the GZ/RS/X4/X6 arms.

Run from this directory (or set `PYTHONPATH=.`):

```bash
python run_s_j1.py dev
python run_s_j1.py virgin-metrics
python run_s_j1.py virgin-predict --arm GZ
```

The virgin command reads only arms passing the computed dev gate and writes the frozen result, parameter, and prediction artifacts.
