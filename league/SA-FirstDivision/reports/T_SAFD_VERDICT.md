# Verdict — T-SAFD total shots — FAIL (dev gate)

Dev used 90 warm-up and 214 scored 2025/2026 matches. The 94-match
2026/2027 TRANSITIONAL virgin was deliberately unread because all arms
failed the dev gate.

| Arm | Dev pooled LL@23.5 | Outcome |
|---|---:|---|
| A | 0.677011 | FAIL: above naive 0.664171 |
| B | 0.676045 | FAIL: above naive 0.664171 |
| C | 0.676726 | FAIL: above naive 0.664171 |
| League base | 0.703122 | baseline |
| Naive trailing-10 | 0.664171 | baseline |

No arm reads virgin or ships. `fitted_params_virgin.json` is an
explicit unfitted stub with `training_rows: 0`; no prediction CSV was
written. The arm outcomes are FAIL at dev, not clean or provisional;
the reference-arm and both-pass/tie virgin rules are not invoked.
Verification: dev n=214 after a 90-match tuning block, only regular
non-awarded rows were loaded, and no 2024/2025 or 2026/2027 rows were
read during dev. (Independent replay from the engine code reproduces
the tuning — lambda 100.0, r_A 57.813078, level cell [30.0, 0.5, 50.0]
— and every dev LL exactly.)

Verifier's note (coordinator, 2026-11-10): the engine is a verbatim
copy of the SA reference, and three SA values were NOT adapted to
this prereg — all verdict-immaterial, recorded for the fix before any
future confirmatory read: (1) ladder lines are (23.5, 24.5, 25.5),
not the prereg's 22.5/23.5/24.5 (gate at 23.5 unaffected); (2) the
half split in fitted_params.json / write_predictions is 0.4559, not
the frozen 0.4557 (never used — no predictions were written);
(3) the tuning key "lambda_logloss_24_5" mislabels a value computed
at 23.5 (the lambda choice, 100.0, stands). Two further reference
vs prereg mismatches, also verdict-immaterial: the league baseline is
the SA port's Poisson-with-decay-weighted-league-mean, not the
prereg's expanding over-23.5 rate — recomputed prereg-literal base
0.702139 vs harness 0.703122, models beat both either way; and
state updates are per-match, not date-grouped as the prereg says —
any same-date leakage flatters the models, which still fail by
~0.012 LL against the naive (0.664171). FAIL is robust under every
reading. The prereg text is left frozen; fix these constants before
any confirmatory virgin read.
