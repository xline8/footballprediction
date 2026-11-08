# C-KR verdict

Dev n=684 at primary 8.5. Gate Zero LL 0.703866 beats league base 0.720124 and naive trailing-10 0.716360. X7 LL 0.706735 also beats both baselines. Virgin n=228: both arms LL 0.683428 versus best baseline 0.759362 and Gate Zero 0.683428; calibration diff is -5.5224pp, SE 3.2658pp, exceeding the provisional limit (1pp + 1 SE). X7 also fails the per-season sign check. No arm ships.

Virgin was read only for the two dev-passing arms. Outputs are in `engine/corners/results_dev.json` and `results_virgin.json`; no fitted params and no prediction CSV (FAIL).
