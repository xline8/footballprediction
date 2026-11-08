# Verdict — G-IN (India Indian Super League goals)

**FAIL at the dev gate. Virgin 2025/2026 deliberately NOT read.
Nothing ships.**

## Dev (walk-forward, scored 2022/2023–2024/2025, n=419; pooled)

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | 1.0564 | 0.2317 | 0.7041 |
| SHRINK | 1.0564 | 0.2317 | 0.7041 |
| X3 | 1.0874 | 0.2392 | 0.7162 |
| Climatology (baseline) | 1.0628 | 0.2360 | 0.6854 |

## Gate arithmetic (frozen legs, applied mechanically)

- Dev gate requires pooled 1X2 LL **and** RPS to beat climatology
  **and** OU2.5 LL to beat the base-rate baseline. Gate Zero wins
  the 1X2 legs (1.0564 < 1.0628; RPS 0.2317 < 0.2360) and loses
  the OU leg outright (0.7041 > 0.6854) — the program's recurring
  goals failure mode (G-J2, G-J3, G-DK, G-AU, …). Arm dead.
- SHRINK is **byte-identical to Gate Zero** on every dev row: under
  season-blocked fitting the 1–5-prior-match band never occurs at
  prediction time (the DK degeneracy, recorded in the prereg in
  advance). It therefore fails the same leg; its real test case
  (Inter Kashi / SC Delhi debuting in the virgin) never arrives
  because the gate stops the candidate first — reported as a
  construction fact, not repaired mid-flight.
- X3 (set-play decomposition) is worse than Gate Zero on all
  three metrics despite its adopted trait (F5, r=0.489).
- Gate Zero failed its dev gate ⇒ variants moot, verdict FAIL,
  virgin NOT read (`engine/goals/results_virgin.json` records
  `virgin_read: false`). The F11 caveat (FotMob xG runs ~19% low
  in this league) stands as a documented suspicion for the OU
  failure, not an excuse: the gate is the gate.

## What ships

Nothing. 2025/2026 remains the virgin for one future read under a
new prereg; 2026/2027 confirmatory untouched.
