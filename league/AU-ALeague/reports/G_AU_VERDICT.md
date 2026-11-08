# G-AU verdict — FAIL

Prereg: `prereg/PREREG_G_AU.md` (frozen in commit b353f24, before
any fitting). Dev = walk-forward evaluation seasons
2022/2023–2024/2025 (pooled n = 508); virgin = 2025/2026.

## Dev results (pooled)

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | 1.0737 | 0.2311 | 0.6705 |
| SHRINK | 1.0737 | 0.2311 | 0.6705 |
| X3 | 1.0867 | 0.2354 | 0.6750 |
| Climatology (baseline) | 1.0845 | 0.2347 | 0.6675 |

## Gate arithmetic

Dev gate requires pooled 1X2 LL **and** RPS to beat climatology
**and** OU2.5 LL to beat the base-rate baseline. Gate Zero passes
the 1X2 leg (1.0737 < 1.0845) and the RPS leg (0.2311 < 0.2347)
but **fails the OU leg: 0.6705 > 0.6675**. Gate Zero is dead at
the dev gate. Per the prereg the variants are moot and **the
virgin window was deliberately NOT read**
(`results_virgin.json` records `{"virgin_read": false, "reason":
"gate zero failed dev gate"}`; 2025/2026 stays usable only under
a future new prereg's terms, and 2026/2027 remains untouched as
the confirmatory window).

## Verification finding (recorded plainly)

The SHRINK arm is **identical to Gate Zero in every dev row** —
the degeneracy the prereg recorded in advance from the DK build:
under season-blocked fitting a team in target season S has either
0 prior in-league matches (newcomer — Auckland FC in 2024/2025;
n/6 = 0 ⇒ league-mean ratings, exactly Gate Zero's unseen rule)
or a full history. The 1–5-match band never occurs, so the arm
cannot bite in this harness; a biting version needs per-match
refit cadence = a NEW prereg. X3 (SHRINK + the set-play tilt,
with AU's program-strongest set-play trait r = 0.724) differs
and is worse on every dev metric — no arm was close to rescuing
the candidate.

**Verdict: FAIL. Nothing ships.** No predictions CSV, no fitted
virgin parameters. The pattern matches G-DK and G-J2: the DC
blend prices 1X2/RPS better than climatology and the OU2.5 total
marginally worse than the prior-seasons base rate.
