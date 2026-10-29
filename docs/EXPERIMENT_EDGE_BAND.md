# Experiment: Re-validating the Live-Pick Edge Band

Experiment and verdict only. Production was not changed: `make_picks_live.py`
still uses `EDGE_LO/EDGE_HI = 0.20/0.22` and `ODDS_LO/ODDS_HI = 1.20/1.50`.

**Question.** Does the production edge band correspond to a real edge?

Setup:

- Edge = `p_meta(home) − p_fair_shin(home)`, on B365 opening odds.
- Home wins only, flat 1u stake, settled at `odds_open`.
- Meta model: 9-logit, monthly walk-forward, leak-free; records mode `blend`.
- Diagnostics on 2017/18–2022/23 produced a threshold grid; two rules were
  then tested on the 2023/24–2025/26 confirmation window.

## Results

| Metric | Value |
|---|---|
| Home-win candidates, top-5 leagues | 15,494 |
| Edge distribution, all seasons | mean −0.0023, std 0.0123, max +0.0832 |
| Fraction of candidates with edge ≥ 0.05 | 0.0014 (0.14%) |
| Fraction with edge ≥ 0.10 | 0.0000 |
| Fraction with edge ≥ 0.20 | 0.0000 |

In the diagnostics window, every threshold at or above 0.05 produced fewer
than 100 picks, and thresholds at or above 0.10 produced none. No threshold
met the pre-set criterion of at least 100 diagnostic picks, so no candidate
replacement threshold (T*) was evaluated.

## The production band (R1)

- Historical frequency: **0 picks** across all 68,763 records, all seasons.
- Confirmation window: n = 0, yield not applicable.

## Verdict

**UNVALIDATED.** The production band, edge in [0.20, 0.22), describes an
event that effectively never occurs: the largest edge observed anywhere in
the walk-forward history is +0.083. The live filter never fires, so it
exploits no edge, and there is nothing to replace, since no alternative
threshold qualifies either.

This confirms the warning recorded in `make_picks_live.py` on 2026-10-26:
with correct Shin de-vigging, an edge of 0.20 or more on 1.2–1.5 favourites
does not appear. The result is consistent with the project's broader 1X2
market-efficiency finding: no tested rule produces a statistically
significant positive ROI.
