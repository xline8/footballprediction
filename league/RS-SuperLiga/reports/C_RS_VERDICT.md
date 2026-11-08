# Verdict — C-RS (RS-SuperLiga corners): **NOT BUILT (feasibility)**

Frozen decision: PREREG_C_RS.md (branch `wip-rs-superliga`, commit
a0b379d, before any fitting).

No model was fitted, no dev gate was run, and the virgin was not read for
corners. Reason, in one paragraph: corners exist only in the virgin
season itself (2025/2026, 9.003/match inventory level) — the stats feed
is absent in every dev season (2021/2022–2024/2025: 0 stats rows in 1,192
matches), so there is no dev corners series at all. The X7 box-touches /
territory input is virgin-only, and even the FI possession-only fallback
is unavailable because `BallPossesion` is also virgin-only. A dev gate
can only validate an arm against the same quantity it would ship against,
and that quantity exists in exactly zero dev seasons. This is a
feasibility verdict recorded pre-fitting, not a gate FAIL. C-RS may be
pre-registered fresh once stats-era dev seasons exist; it may not be
rescued inside this prereg.
