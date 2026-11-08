# G-DE2 verdict — FAIL (dev gate; virgin NOT read)

Prereg: `prereg/PREREG_G_DE2.md` (frozen 4261ad8, before any fitting).
Dev = walk-forward evaluation seasons 2022/2023–2024/2025 (pooled
n = 918); virgin = 2025/2026 (n = 306, complete) — **not read**,
because Gate Zero fails its own dev gate (below).

## Dev results (pooled)

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | 1.0580 | 0.2247 | 0.6995 |
| SHRINK | 1.0580 | 0.2247 | 0.6995 |
| X2 (mover, direction-specific) | 1.0492 | 0.2218 | 0.6967 |
| X3 (set-play, on SHRINK) | 1.0722 | 0.2293 | 0.7069 |
| Climatology (baseline) | 1.0742 | 0.2308 | 0.6757 |

## Gate arithmetic

- 1X2 LL and RPS legs: every arm beats climatology (X2 by the
  widest margin). Those legs pass.
- **OU2.5 leg: EVERY arm fails.** Gate Zero's OU LL (0.6995) is
  worse than the base-rate baseline (0.6757) by 0.0238; X2, the
  best arm on every metric, still fails it (0.6967 > 0.6757);
  X3 is worst (0.7069). Per season, the model's OU LL loses to the
  base rate in 2022/2023 (0.7196 vs 0.6813) and 2023/2024 (0.7101
  vs 0.6706) and wins only in 2024/2025 (0.6688 vs 0.6751).
- Mechanical reading (prereg): Gate Zero fails its dev gate ⇒
  variants are moot, verdict FAIL, **virgin NOT read**. The
  harness records this itself: `engine/goals/results_virgin.json`
  = `{"virgin_read": false, "reason": "gate zero failed dev gate"}`.

## Recorded plainly

- **X2 works on 1X2 and still cannot ship.** The mover arm is
  identical to Gate Zero in 2022/2023 by construction (no prior
  transitions in-corpus), then improves 1X2 LL in both seasons
  where it bites (2023/2024: 1.0403 vs 1.0532; 2024/2025: 1.0722
  vs 1.0855) and RPS likewise — the direction-specific offsets
  (up −0.36/+0.14, down +0.10/+0.08 goals, estimated in-fit)
  carry real signal. It dies with everything else on the OU leg:
  in this league the DC blend's *total-goals* distribution is
  worse than a constant base rate in two of three dev seasons,
  even while its 1X2 ranking is clearly better. A ranking model
  whose totals are mispriced — the mirror of G-BE, which passed
  dev and died on virgin OU calibration.
- SHRINK is identical to Gate Zero in every row — the same
  construction fact BE/DK/CH recorded: under season-blocked
  fitting the 1–5-match band never occurs.
- X3 (set-play tilt) hurts everywhere in DE-2 (pooled 1X2 LL
  1.0722, sign 0/3 by inspection of the per-season rows) despite
  the trait's solid reliability (r = 0.558).

**Verdict: FAIL. Nothing ships. Virgin deliberately unread.**
Builder verification: dev rerun reproduces `results_dev.json`
exactly; X2's offset wiring and orientation were read line-by-line
against the prereg (see the engine commit message for the Codex
commit incident and its resolution).
