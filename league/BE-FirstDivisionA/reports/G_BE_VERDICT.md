# G-BE verdict — FAIL

Prereg: `prereg/PREREG_G_BE.md` (frozen f0c214a, before any fitting).
Dev = walk-forward evaluation seasons 2022/2023–2024/2025 (pooled
n = 956); virgin = 2025/2026 (n = 313), read once, for all three
dev-passing arms.

## Dev results (pooled)

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | 1.0024 | 0.2046 | 0.6828 |
| SHRINK | 1.0024 | 0.2046 | 0.6828 |
| X3 | 1.0186 | 0.2088 | 0.6865 |
| Climatology (baseline) | 1.0765 | 0.2300 | 0.6884 |

All three arms beat climatology on 1X2 LL and RPS and beat the
base rate on OU2.5 LL → all pass the dev gate (X3's OU margin is
thin: 0.6865 vs 0.6884). G-BE is the first conveyor goals candidate
whose Gate Zero clears the dev gate outright.

## Virgin results (2025/2026, n = 313)

| Arm | 1X2 LL | RPS | OU2.5 LL | Cal: home-win | Cal: OU2.5 |
|---|---|---|---|---|---|
| Gate Zero | 1.0417 | 0.2191 | 0.7003 | +3.02pp (SE 2.67) | +4.95pp (SE 2.84) |
| SHRINK | 1.0417 | 0.2191 | 0.7003 | +3.02pp (SE 2.67) | +4.95pp (SE 2.84) |
| X3 | 1.0550 | 0.2233 | 0.7094 | +3.31pp (SE ~2.7) | +6.02pp (SE ~2.8) |
| Climatology | 1.0829 | 0.2331 | 0.7001 | — | — |

## Gate arithmetic

- Leg (i): Gate Zero passes (1.0417 ≤ climatology 1.0829). X3 fails
  (1.0550 > Gate Zero's 1.0417).
- Leg (ii): home-win breach 2.02pp beyond the 1.0pp boundary is
  within 1 SE (2.67) → provisional on that sub-leg; **the OU2.5
  breach is 3.95pp beyond the boundary, beyond 1 SE (2.84) →
  FAIL.** The virgin season cooled (2.67 goals/match vs dev ~2.87)
  and the blend over-predicted the over-rate by ~5pp.
- Leg (iii): X3's dev sign check vs Gate Zero is **0/3** (worse in
  every dev season) — it could not have shipped in any case.

## Verification finding (recorded plainly)

The SHRINK arm is **identical to Gate Zero in every dev and virgin
row** — the same construction fact DK and CH recorded: under
season-blocked fitting, a team in target season S has either 0
prior in-league matches (newcomer; n/6 = 0 ⇒ league-mean ratings,
exactly Gate Zero's unseen rule) or a full prior season (factor 1).
The 1–5-match band never occurs, so the arm cannot bite in this
harness.

**Verdict: FAIL. Nothing ships.** The DC blend prices 1X2 well in
Belgium (virgin LL clearly beats climatology) and still dies on
OU calibration — the mirror image of G-CH, which died at the dev
OU leg instead.
