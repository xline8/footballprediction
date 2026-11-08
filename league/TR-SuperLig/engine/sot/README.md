# S-TR shots-on-target engine

This is the league-local implementation of the frozen S-TR preregistration. It uses the v5 decayed ratings, Newton ridge regression, trailing-10 naive tracker, negative-binomial line probabilities, and the GZ/RS/X4 arms.

Run from this directory (or set `PYTHONPATH=.`):

```bash
python run_s_tr.py dev
python run_s_tr.py virgin-metrics
python run_s_tr.py virgin-predict --arm GZ
```

The virgin command reads only arms passing the computed dev gate and writes the frozen result, parameter, and prediction artifacts.
