# K-CO join proof report — run 3 continuation

Date: 2026-11-12. Branch: `build/lane1-kco`. Verdict: **MERGE-READY**.

## Runner pair

- Both completed with exit 0 under `MALLOC_ARENA_MAX=2` using the main checkout `.venv`; run 1 duration 1,957 seconds and run 2 duration 1,762 seconds.
- 62 leagues / 123 markets. Run 1: 13,521 predictions, 0 settled, 0 errors. Run 2: 13,520 predictions, 0 settled, 0 errors. The one-prediction difference is the adjudicated AR duplicate removal below.
- CO-PrimeraA: 10 upcoming fixtures and 40 predictions (10 per market: SOT, corners, total shots, cards) in each run; 0 errors and 0 settled.
- Run 1 fetched_new was 2,092 for the already-fresh J1 store and 0 for every other league. Run 2 fetched_new was 0 for all 62 leagues.

## Byte comparison

The snapshots contain 397 files each. `diff -rq run1 run2` found 3 differing files: 2 prediction CSVs and `run_log.jsonl`; 394 files were byte-identical. The two prediction diffs are explained by the coordinator’s independently verified live-feed adjudication below. Evidence: `/home/hatch/workspace/kco-proof/diff_run1_run2.txt`.

Coordinator verdict on the byte-compare diffs (verbatim):

1. AR-PrimeraBNacional cards, fixture 6575527 removed: FotMob had listed the SAME match twice in run 1 — 6546950 and 6575527, both Godoy Cruz vs Tristán Suárez, 2026-11-15, exp_total 4.534103008820326 bit-equal, referee Maximiliano Ramírez, n_prior 0, multiplier 1.0. Between the runs FotMob removed the duplicate 6575527 from its leagues listing (verified live: neither season 2025 nor 2026 allMatches contains it; 6546950 remains with bit-equal predictions). Live-feed duplicate removal, not a runner defect.
2. AR cards, fixture 6546956: FotMob moved its date 2026-11-15 -> 2026-11-16 (verified live: leagues endpoint utc=2026-11-16T01:30:00Z). Same referee Maximiliano Manduca, same n_prior 29; numeric shifts max 0.0000244 (multiplier), p_over_4.5 0.4810598 -> 0.4810618 (delta 2e-6), chosen side unchanged (under 0.5 both runs). Live-feed date move, same category as the BR-SerieB 5190810 precedent in the K-FO proof.
3. ZA-PSL corners: 20 differing rows, 0 numeric field diffs across 160 rows — name-only 'AmaZulu' -> 'AmaZulu FC'. Known FotMob spelling flip; values bit-equal.

## CO checks

An independent separate-process recompute through the current runner adapters, using the live 10-fixture pull and run-2 CSVs, matched all 40 rows. SOT, corners, total shots, and cards each had 10 expected / 10 recomputed rows, 0 differing fields, and maximum absolute float difference 0.0.

The amended cards history loader returns exactly 1,336 rows for the six frozen dev-era seasons (2023 Apertura through 2025 Clausura), matching the frozen harness expectation. The full live CSV has additional virgin/current rows as expected.

HEAD-vs-amended `predict_cards` inertness probes used 8 fixed fixtures each: AR-PrimeraBNacional `x8` produced 8/8 rows byte-identically; AU-ALeague `gate_zero` produced 8/8 rows byte-identically.

## Synthetic settlement

Match 5121316 (2026-01-16, Deportivo Pereira–Llaneros FC) was verified to have complete event-unified actuals: home 3, away 2, total 5. The adapter prediction was exp_total 5.9211786468235115, p_over_5.5 0.5349248703199728, multiplier 1.0. `settle()` settled exactly once on the first pass (`1`) and nothing on the second (`0`). The four touched artifacts were restored byte-identically, including the pre-existing/absent file states.

## Gate and README

The referee gate remains the coordinator’s passed 2/10 result from 2026-11-12 16:58 WIB: Deportivo Pasto–Junior FC (match 1000014235, Diego Alejandro Ruíz Casas) and Llaneros FC–Chicó FC (match 1000014232, Carlos Márquez). The CO paragraph in `league/runner/README.md` is updated from PREPARED BUT BLOCKED to joined, PROVISIONAL state with these proof results. No sealed data was read and the main checkout was not touched.
