# Verdict — T-SK (SK-1Liga total shots)

**NOT BUILDABLE — no prereg, no fitting, virgin NOT read.**

The candidate fails the template's feasibility condition: a valid
virgin window must contain the target *under the same definition*
as the dev window. Here the target's counting changes at exactly
the rich-feed boundary where the virgin window begins:

| Season | Mean total shots / match |
|---|---|
| 2021/2022 | 19.82 |
| 2022/2023 | 20.22 |
| 2023/2024 | 17.80 |
| 2024/2025 | 19.24 |
| 2025/2026 (virgin) | **27.10** |
| 2026/2027 | **29.12** |

(+~40% dev→virgin, while goals, SOT and corners are continuous
across the same boundary — EDA F1.) A dev→virgin gate on the raw
series would test the feed change, not a model. The
total-minus-blocked reconstruction cannot be verified against
dev-era data (blocked/off-target components are not stored in the
dev era — the rich stat set exists only from 2025/2026), so it is
recorded as considered-and-rejected, exactly as in CZ-Liga and
RO-LigaI. Team total-shots traits are in fact reliable inside the
dev era (EDA F2: r = 0.729 / 0.623) — if FotMob's counting is ever
backfilled consistently, this candidate can be re-registered with
a fresh prereg and a fresh virgin window.
