# Verdict — S-RS (RS-SuperLiga shots on target): **NOT BUILT (feasibility)**

Frozen decision: PREREG_S_RS.md (branch `wip-rs-superliga`, commit
a0b379d, before any fitting).

No model was fitted, no dev gate was run, and the virgin was not read for
shots on target. Reason, in one paragraph: ShotsOnTarget exists only in
the virgin season itself (2025/2026, 8.831/match inventory level) — the
stats feed is absent in every dev season (2021/2022–2024/2025: 0 stats
rows in 1,192 matches), so there is no dev SOT series at all, and the X4
on-target-ratio input is impossible (no shotmap and no xG in any season).
A dev gate can only validate an arm against the same quantity it would
ship against, and that quantity exists in exactly zero dev seasons. This
is a feasibility verdict recorded pre-fitting, not a gate FAIL. S-RS may
be pre-registered fresh once stats-era dev seasons exist; it may not be
rescued inside this prereg.
