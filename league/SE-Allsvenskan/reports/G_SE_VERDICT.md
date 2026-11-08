# G-SE verdict — FAIL

Prereg: `league/SE-Allsvenskan/prereg/PREREG_G_SE.md` (frozen in
commit 62320f5, before any fitting). Dev = walk-forward evaluation
seasons 2022–2024 (pooled n = 720); virgin = 2025.

## Dev results (pooled)

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | 1.0295 | 0.2215 | 0.6918 |
| SHRINK | 1.0295 | 0.2215 | 0.6918 |
| X3 | 1.0412 | 0.2242 | 0.6947 |
| Climatology (baseline) | 1.0587 | 0.2338 | 0.6911 |

## Gate arithmetic

Dev gate requires pooled 1X2 LL **and** RPS to beat climatology
**and** OU2.5 LL to beat the base-rate baseline. Gate Zero passes
the 1X2 leg (1.0295 < 1.0587) and the RPS leg (0.2215 < 0.2338) but
**fails the OU leg: 0.6918 > 0.6911** (by 0.0007 — close, and still
a fail; gates are not moved). Gate Zero is dead at the dev gate.
Per the prereg's NOT-built clause the variants are moot and **the
virgin window was deliberately NOT read** (`results_virgin.json`
records `{"virgin_read": false, "reason": "gate zero failed dev
gate"}`; 2025 stays usable only under a future new prereg's terms,
and 2026 remains untouched as the confirmatory window).

## Verification finding (recorded plainly)

The SHRINK arm is **identical to Gate Zero in every dev row** —
the same construction fact the coordinator caught in DK: under the
prereg's season-blocked fitting, a team in target season S has
either 0 prior in-league matches (newcomer; n/6 = 0 ⇒ league-mean
ratings, exactly Gate Zero's unseen rule) or ≥240 (returning team;
factor 1). The 1–5-match band the arm was written for never occurs,
so the arm cannot bite in this harness. A shrinkage arm that bites
would need a per-match refit cadence — a different protocol,
requiring a NEW prereg, not a repair of this one. X3 (SHRINK + the
set-play tilt) does differ and is worse on dev (1X2 LL 1.0412; OU
0.6947; per-season 1X2 LL worse than Gate Zero in 2023/2024), so no
arm was close to rescuing the candidate.

**Verdict: FAIL. Nothing ships.** No predictions CSV, no fitted
virgin parameters. As in DK and G-J2, the DC blend prices the 1X2
market well and the OU2.5 total marginally worse than the
prior-seasons base rate.
