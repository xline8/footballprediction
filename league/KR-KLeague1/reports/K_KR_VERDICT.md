# K-KR verdict

Dev n=684 at primary 3.5. Gate Zero model LL 0.686354 beats base 0.690860 and naive 0.702985. X8 model LL 0.681587 beats both. Virgin n=228: Gate Zero LL 0.676491 versus Gate Zero baseline 0.689239 and best baseline 0.689239; calibration diff -1.7397pp, SE 3.2622pp, provisional pass. X8 LL 0.679699, calibration diff -1.5309pp, SE 3.2734pp, provisional pass, but it does not improve the Gate Zero virgin LL. Gate Zero ships by lower LL/tie-break rule.

Referee coverage was 64/228; X8 recorded 164 unknown-identity and 8 thin-history fallbacks. Outputs are in `engine/cards/results_dev.json`, `results_virgin.json`, `fitted_params_virgin.json`, and `predictions/k_kr_virgin_predictions.csv`.

Artifact note (coordinator verification, 2026-11-09): the shipped
predictions CSV was first written with the SE halves constant (0.370)
hard-coded in the ported harness. The FT probabilities were unaffected;
the presentation columns (mean_1h/mean_2h) were regenerated with the
frozen KR constant 0.350/0.650 and the harness source corrected. The
virgin was not re-read; gate arithmetic above is unchanged and was
independently recomputed from the shipped CSV (LL 0.676491, breach
-1.74pp, SE 3.26pp — exact).
