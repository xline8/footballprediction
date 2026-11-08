# Fix round — P5 Gate Zero runner honesty + goals schema

Repo: ~/workspace/footballprediction. NEVER git commit/push. Modify ONLY
league/gate_lib/ and league/improvement_scratch/P5/. Coordinator verification found
defects in run_gate_zero.py / reproduce.py output. Fix all of them:

1. GOALS DEV SCHEMA (currently "unsupported result schema" for G-AE, G-SCO, G-TR):
   goals results_dev.json is either a top-level LIST of row dicts (SCO, TR) or
   {"protocol":..., "rows":[...]} (AE). Row fields: n, ll_1x2, rps, oull_2_5, arm,
   season (incl. a "pooled" row), kind ("model" | "climatology" | "naive" if present).
   Support it generically in reproduce.py: per arm+kind, recompute pooled ll_1x2, rps
   and oull_2_5 as the n-weighted mean of the per-season rows and compare against the
   persisted "pooled" row (that's the shipped value). Emit one reproduction.csv row per
   (arm, kind, metric) pooled value plus per-season rows are optional. Baselines for
   goals = the non-model kinds. G-AE must end with real reproduced dev rows, not 0.

2. PER-MATCH VIRGIN ROWS MUST COMPARE (currently G-SCO/G-TR rows say PASS with empty
   value_shipped/abs_delta): for every sampled candidate, fill value_shipped from
   results_virgin.json for the shipped/reference arm and set abs_delta + match honestly:
   - counting markets: shipped LL = ll_<primary> (or metrics ll at primary), shipped
     calibration = calibration_diff / calibration fields, converting fractions to pp
     (x100) where the artefact stores fractions, and translating sign when the artefact's
     stated/stored convention is actual - predicted (record a SIGN_CONVENTION note).
   - goals: shipped OU LL = oull_2_5 of the gate_zero/model entry in results_virgin.json;
     shipped calibration = calibration.over25_diff (fraction -> pp; SCO stores
     -0.012490486645276078 = -1.249pp under predicted - actual, which matches a
     per-match recompute of -1.2490486645276124pp — verify, don't assume).
   A per-match row may only be PASS when abs_delta <= 5e-7.

3. NO TAUTOLOGICAL ROWS: rows currently sourced "virgin_aggregate" copy the persisted
   aggregate as both recomputed and shipped (delta 0.0 by construction). Replace them
   with LEG-DECISION rows: recompute the decision from the persisted aggregates via
   gate_lib.metrics and compare the DECISION against the shipped verdict's outcome:
   - dev_pass per arm (pooled dev LL < both baselines) vs the verdict's dev outcome
     (arms that were/were not read on virgin, candidate dev FAIL/PASS);
   - leg (i) pass/fail per virgin-read arm (virgin LL <= reference arm and <= best
     baseline) vs verdict;
   - leg (ii) calibration band (PASS/PROVISIONAL/FAIL) per virgin-read arm vs verdict;
   - sign check (wins/n vs reference arm) where per-season dev LLs exist, vs verdict.
   Encode shipped decisions in the runner from the verdict files' stated outcomes —
   read them from the classification in league/audit_scratch/class_batch*.jsonl
   (outcome + fail_point + fail_legs per candidate) PLUS, for per-arm decisions, a small
   explicit per-candidate table in the runner transcribed from the verdict .md files
   (cite the verdict file in the row notes). CSV columns stay the same; for decision
   rows put the decision strings in value_recomputed/value_shipped and match=PASS/FAIL.
   Keep genuine value-recompute rows (dev per-season->pooled, per-match virgin) as the
   only rows claiming numeric reproduction; set their notes to say which level they are:
   L1 per-match, L2 per-season->pooled.

4. REPORT REWRITE (gate_zero_report.md): headline verdict must distinguish levels:
   L1/L2 numeric reproductions (count, all within 5e-7 or list failures), L3 leg-decision
   reproductions (count, agreements/disagreements). Gate Zero PASS iff all L1/L2 values
   reproduce within criterion AND all L3 decisions agree; state any NOT_REPRODUCIBLE legs
   explicitly per candidate with reasons. Keep sample table, guard demonstrations,
   constants demonstration, limitations. No shipped verdict changes.

5. Re-run tests + runner; print the final per-candidate counts.
