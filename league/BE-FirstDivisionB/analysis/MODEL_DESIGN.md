# Phase A — Model Design

No fitting is performed in Phase A.

## G-BEB goals — BUILDABLE

Reference: goals-only Dixon–Coles production pattern. Arms are Gate Zero (goals-only DC), SHRINK (BE-A PREREG_G_BE arm 2 verbatim in form), and X2 (SHRINK plus the mover prior in the J1 PREREG_G_J1 arm-2 form, with magnitudes frozen from this league’s mover EDA).

Dev seed: 2021/2022. Evaluation seasons: 2022/2023, 2023/2024 and 2024/2025, n=654. Virgin: 2025/2026, n=278, read once only for dev-passing arms. 2026/2027, n=70, is reserved and not read. Primary metrics are 1X2 log loss/RPS and OU2.5 log loss versus climatology, using the BE-A G gate legs verbatim.

All phases are ordinary rows, with phase flagged and no phase feature.

## S-BEB / C-BEB / K-BEB / T-BEB — NOT BUILDABLE

SOT, corners, cards and total shots exist only in the 2025/2026 virgin and partial 2026/2027. There is no scorable dev window. No fitting on either virgin or reserved data is proposed.

Cards artefact (recorded in EDA.md): the stats feed undercounts
yellows one-directionally vs the event feed (exact agreement 72.20%,
stats lower in 27.80%, never higher, mean -0.3466/match, mechanism
verified on payloads). The presumptive target for a future prereg is
event-unified - but the dev-era event feed is too sparse to score
(32-60 matches/season carry any Card event), so K-BEB is NOT
BUILDABLE under either source.

Halves are presentation-only: goals use the frozen constant and count markets have null halves constants.

