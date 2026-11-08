# RESULT — RS-SuperLiga (Serbia Super Liga, FotMob 182)

`[Muse-2]` to `[Jarvis]`. Full league dir in `outbox-muse2/RS-SuperLiga/`.
Prereg: branch `wip-rs-superliga`, commit a0b379d (before any fitting).

## Verdicts

| Candidate | Verdict |
|---|---|
| G-RS goals | **FAIL (dev gate, OU leg)** — Gate Zero pooled OU2.5 LL 0.698890 vs climatology 0.695516; 1X2 LL 0.992930 and RPS 0.207218 both beat climatology (1.064029 / 0.233579). Virgin NOT read. Nothing ships. |
| S-RS shots on target | **NOT BUILT (feasibility)** — SOT exists only in the virgin season; zero dev seasons. |
| C-RS corners | **NOT BUILT (feasibility)** — corners exist only in the virgin season; X7 and the possession fallback both virgin-only. |
| K-RS cards | **NOT BUILT (feasibility)** — no usable yellows target: dev event feed YellowRed-only (0.041–0.120/match), stats feed virgin-only and undercounts events by 0.432/match. |
| T-RS total shots | **NOT BUILT (feasibility)** — total shots exist only in the virgin season; zero rich-era dev seasons (FI T-FI precedent, stronger). |

## Virgin numbers

None. No candidate passed dev, so per the prereg the virgin season
(2025/2026, n=296) was **never read for any candidate** — there are no
virgin metrics to report, and no `results_virgin.json` from a run (the
file in `engine/goals/` is an audit record stating `virgin_read: false`).
The confirmatory reserve 2026/2027 was untouched. Inventory levels only
(never used for fitting or gating): virgin goals 2.662/match, SOT 8.831,
corners 9.003, total shots 25.084, event yellows 4.662.

## Dev numbers (G-RS, season-blocked, pooled n = 888 league-member rows)

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | 0.992930 | 0.207218 | 0.698890 |
| SHRINK | 0.992930 | 0.207218 | 0.698890 (identical to Gate Zero — no team ever in the 1–5 prior-match band) |
| X2 | 0.986856 | 0.205114 | 0.696747 |
| Climatology | 1.064029 | 0.233579 | 0.695516 |

OU leg fails in 2023/2024 (0.715397 vs 0.699363); it passes in the other
two dev seasons. X2 fires only in 2024/2025 (4 completed entrant
transitions) and improves all three metrics there, but pooled it still
fails the OU leg — and variants are moot once Gate Zero fails dev.

## What Jarvis should check

1. **The era break** — the whole league turns on it: stats feed absent in
   all 1,192 dev matches, rich only from the virgin season itself. Verify
   from `analysis/eda_summary.json` (`levels`, `traits_dev`) and the raw
   JSONs: `content.stats.Periods` is empty before 2025/2026.
2. **The dev-gate OU failure** — recompute the climatology baseline from
   `data/rs_matches.csv` (an independent recheck already matched the
   harness to all six printed digits: 1.064029 / 0.233579 / 0.695516).
   The failure is narrow pooled (0.003374) but the gate is binary and
   frozen; confirm no gate was moved.
3. **Virgin discipline** — confirm the virgin was not read: `engine/goals/`
   has no virgin code path (no `virgin_metrics`, no predictions writer),
   the dev loader refuses 2025/2026 and 2026/2027 rows, and no
   `predictions/` directory exists. The only 2025/2026 numbers anywhere
   are EDA inventory levels.
4. **Prereg ordering** — prereg commit a0b379d on `wip-rs-superliga`
   predates all engine artifacts; `engine/goals/dc.py` is byte-identical
   to the FI reference (md5 bcf5e7e6de27e790bf85a1facb296e5d).
5. **The not-built rulings** — S/C/K/T are feasibility verdicts, not gate
   FAILs; each prereg + verdict file states the zero-dev-season evidence.
   K-RS deserves a second look if a future feed fixes the dev cards feed,
   but it may not be rescued inside this prereg.
