# G-DK verdict — FAIL

Prereg: `league/DK-Superligaen/prereg/PREREG_G_DK.md` (frozen in
commit 6a0240b, before any fitting). Dev = walk-forward evaluation
seasons 2022/2023–2024/2025 (pooled n = 579); virgin = 2025/2026.

## Dev results (pooled)

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | 1.0626 | 0.2215 | 0.6948 |
| SHRINK | 1.0626 | 0.2215 | 0.6948 |
| X3 | 1.0787 | 0.2264 | 0.6983 |
| Climatology (baseline) | 1.0839 | 0.2292 | 0.6932 |

Per season (Gate Zero model vs climatology OU LL): 2022/2023 0.7038
vs 0.6951; 2023/2024 0.6814 vs 0.6971; 2024/2025 0.6992 vs 0.6873.

## Gate arithmetic

Dev gate requires pooled 1X2 LL **and** RPS to beat climatology
**and** OU2.5 LL to beat the base-rate baseline. Gate Zero passes
the 1X2 leg (1.0626 < 1.0839) and the RPS leg (0.2215 < 0.2292) but
**fails the OU leg: 0.6948 > 0.6932**. Gate Zero is dead at the dev
gate. Per the prereg's NOT-built clause the variants are moot and
**the virgin window was deliberately NOT read** (`results_virgin.json`
records `{"virgin_read": false, "reason": "gate zero failed dev gate"}`;
2025/2026 stays usable only under a future new prereg's terms, and
2026/2027 remains untouched as the confirmatory window).

## Verification finding (recorded plainly)

The SHRINK arm is **identical to Gate Zero in every dev row** — not
a code bug but a construction fact the coordinator caught in
verification: under the prereg's season-blocked fitting, a team in
target season S has either 0 prior in-league matches (newcomer;
n/6 = 0 ⇒ league-mean ratings, exactly Gate Zero's unseen rule) or
≥193 (returning team; factor 1). The 1–5-match band the arm was
written for never occurs, so the arm cannot bite in this harness.
A shrinkage arm that bites would need the v5-style per-match refit
cadence — a different protocol, requiring a NEW prereg, not a repair
of this one. X3 (built on SHRINK + the set-play tilt) does differ
and is worse on dev (1X2 LL 1.0787; OU 0.6983; sign check vs Gate
Zero 0/3 seasons), so no arm was close to rescuing the candidate.

**Verdict: FAIL. Nothing ships.** No predictions CSV, no fitted
virgin parameters. The failure belongs to the reference pattern in
DK: the DC blend prices the 1X2 market well and the OU2.5 total
marginally worse than the prior-seasons base rate — the mirror of
G-J2, where the OU leg also died while 1X2/RPS passed.
