# T-KR verdict

Dev n=684 at primary 23.5. Arms A, B, and C all passed the pooled dev gate against both baselines. Virgin n=228: A/B/C LLs are 0.626950/0.623225/0.623671; best naive baseline is 0.620866. Thus every arm fails the virgin LL leg (and each also exceeds the calibration tolerance: -7.5783pp/-5.4667pp/-6.7536pp versus SEs 3.0494/3.0570/3.0471pp). Nothing ships.

Virgin was read once for A, B, and C as permitted by the dev gate. Outputs are in `engine/total_shots/results_dev.json`, `results_virgin.json`, `fitted_params.json`; no prediction CSV was emitted.

Code note (coordinator verification, 2026-11-09): the ported
total-shots halves split originally read [0.418, 0.543] (SE 2H share
left in place, summing to 0.961); corrected to [0.418, 0.582] in the
engine source. No predictions shipped for T-KR, so no artifact was
affected.
