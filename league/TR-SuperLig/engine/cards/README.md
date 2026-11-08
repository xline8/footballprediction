# K-TR cards engine

Run from the repository root with the project interpreter:

```bash
~/workspace/footballprediction/.venv/bin/python league/TR-SuperLig/engine/cards/run_k_tr.py dev
~/workspace/footballprediction/.venv/bin/python league/TR-SuperLig/engine/cards/run_k_tr.py virgin-metrics
~/workspace/footballprediction/.venv/bin/python league/TR-SuperLig/engine/cards/run_k_tr.py virgin-predict --arm gate_zero
```

The engine is stdlib-only and follows the production cards recipe: 270-day
decayed venue-split team rates, prior 8, and a negative-binomial count model.
The only interpretation choice was to use the CSV `kickoff_utc` as the
canonical ordering key (with `match_id` as the tie-breaker), while referee
history requires strictly earlier kickoff as specified. The extracted table
includes every warehouse-backed TR row, including the separate `2026-2027`
competition; dev and virgin scoring explicitly exclude it.

For the first warm-up observations, a non-positive decayed league component
uses the preregistered fallback mean, since the relative-rate formula would
otherwise divide by zero.
