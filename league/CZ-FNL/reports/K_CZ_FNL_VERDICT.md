# Verdict — K-CZ-FNL (CZ-FNL cards)

**NOT BUILDABLE — no prereg, no fitting, virgin NOT read.**

The candidate fails the template's feasibility condition: the target
must exist in the dev window. Plain-Yellow events — the event-unified
yellows target used by the production cards design — are absent from
the entire dev era and appear only in the virgin season itself.

Payload evidence (matchFacts Card events, per season):

| Season | Plain Yellow | YellowRed | Red |
|---|---:|---:|---:|
| 2021/2022 | 0 | 26 | 17 |
| 2022/2023 | 0 | 19 | 21 |
| 2023/2024 | 0 | 26 | 12 |
| 2024/2025 | 0 | 13 | 22 |
| 2025/2026 (virgin) | 896 | 17 | 18 |
| 2026/2027 (in progress) | 444 | 4 | 9 |

The dev-era feed carries only second yellows and straight reds
(156 card events in 960 matches, 0.16/match) — not a yellow-card target, and not a
proxy for one (a YellowRed is a sending-off, not a yellow count).
The target exists only from 2025/2026, so no dev gate can be run and
no virgin gate can be meaningful: there is nothing to train or test
against before the virgin season. The referee feature (X8) is moot
for the same reason and independently absent: referee names are empty
in all 960 dev-era matches (0 named in 2025/2026 too; 49/111 only
in 2026/2027).

This is the TH-style era flip, stated plainly as a feed fact. The
builder stores per-team `ev_yellow_*` / `ev_yellowred_*` /
`ev_red_*` counts separately (`data/fnl_matches.csv`) — no unified
yellow target is fabricated where plain Yellows do not exist. If
FotMob backfills plain-Yellow events for the dev era, the candidate
can be re-registered with a fresh prereg and a fresh virgin window.
