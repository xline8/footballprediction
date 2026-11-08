# G-CH verdict — FAIL

Prereg: `prereg/PREREG_G_CH.md` (frozen ccf74a9, before any fitting).
Dev = walk-forward evaluation seasons 2022/2023–2024/2025 (pooled
n = 636); virgin = 2025/2026.

## Dev results (pooled)

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | 1.0583 | 0.2185 | 0.7106 |
| SHRINK | 1.0583 | 0.2185 | 0.7106 |
| X3 | 1.0750 | 0.2232 | 0.7222 |
| Climatology (baseline) | 1.0693 | 0.2233 | 0.6918 |

## Gate arithmetic

Dev gate requires pooled 1X2 LL **and** RPS to beat climatology
**and** OU2.5 LL to beat the base-rate baseline. Gate Zero passes
the 1X2 leg (1.0583 < 1.0693) and the RPS leg (0.2185 < 0.2233) but
**fails the OU leg: 0.7106 > 0.6918**. Gate Zero is dead at the dev
gate. Per the prereg, the variants are moot and **the virgin window
was deliberately NOT read** (`results_virgin.json` records
`{"virgin_read": false, "reason": "gate zero failed dev gate"}`;
2025/2026 stays usable only under a future new prereg's terms, and
2026/2027 remains untouched as the confirmatory window).

## Verification finding (recorded plainly)

The SHRINK arm is **identical to Gate Zero in every dev row** — the
same construction fact DK recorded: under season-blocked fitting, a
team in target season S has either 0 prior in-league matches
(newcomer; n/6 = 0 ⇒ league-mean ratings, exactly Gate Zero's unseen
rule) or ≥180 (returning team; factor 1). The 1–5-match band never
occurs, so the arm cannot bite in this harness. X3 (SHRINK + the
set-play tilt, F5 r=0.369) differs and is worse on every dev metric.

**Verdict: FAIL. Nothing ships.** The DC blend prices the 1X2 market
well in Switzerland and the OU2.5 total worse than the prior-seasons
base rate — the same failure shape as G-DK and G-J2.
