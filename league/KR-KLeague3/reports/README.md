# KR-KLeague3 verdicts

Score-only league (FotMob 9537): stats, shotmap, lineup, referee and
xG are absent in all 1,296 payloads, so only the goals candidate was
buildable — and it fails.

| candidate | verdict | virgin |
|---|---|---|
| G-KR3 goals | FAIL (dev gate, all three legs) | NOT read |
| S-KR3 SOT | NOT-BUILDABLE (target absent) | NOT read |
| C-KR3 corners | NOT-BUILDABLE (target absent) | NOT read |
| K-KR3 cards | NOT-BUILDABLE (0 plain Yellows) | NOT read |
| T-KR3 total shots | NOT-BUILDABLE (target absent) | NOT read |

G-KR3 dev (pooled 2022–2024, n=690): Gate Zero 1X2 LL 1.123054 /
RPS 0.239301 / OU 2.5 LL 0.708503 vs climatology 1.090000 / 0.229657 /
0.692295. SHRINK identical (inert). Per-candidate gate arithmetic is
in the `*_VERDICT.md` files here. Nothing ships; no market joins the
daily runner.

The 2025 virgin season is complete (210 matches) and the 2026 season
is in progress (182 played); both are reserved as confirmatory data
for a future prereg. The league build is complete: every buildable
candidate has been through its frozen gate.
