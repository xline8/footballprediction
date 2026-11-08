# Verdict — T-CZ (CZ-Liga total shots)

**NOT BUILDABLE — no prereg, no fitting, virgin NOT read.**

The candidate fails the template's feasibility condition: a valid
virgin window must contain the target *under the same definition*
as the dev window. Here the target's counting changes at exactly
the rich-feed boundary where the virgin window begins:

| Season | Mean total shots / match |
|---|---|
| 2021/2022 | 16.37 |
| 2022/2023 | 18.23 |
| 2023/2024 | 17.72 |
| 2024/2025 | 17.78 |
| 2025/2026 (virgin) | **25.54** |
| 2026/2027 | **28.09** |

(+44% dev→virgin, while goals, SOT and corners are continuous
across the same boundary — EDA F1.) A dev→virgin gate on the raw
series would test the feed change, not a model. The
total-minus-blocked reconstruction cannot be verified against
dev-era data (blocked/off-target components are not stored in the
dev era — the rich stat set exists only in the 388 matches from
2025/2026), so it is recorded as considered-and-rejected, exactly
as in RO-LigaI. Team total-shots traits are in fact reliable
(EDA F2: r = 0.680 / 0.711) — if FotMob's counting is ever
backfilled consistently, this candidate can be re-registered with
a fresh prereg and a fresh virgin window.
