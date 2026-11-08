# Verdict — T-MK (North Macedonia Prva Liga total shots): **NOT BUILDABLE**

No prereg arms exist for T-MK, no engine was built, and no virgin data
was read — there is nothing to fit. (The not-buildable standing is
pre-registered in Phase A: `prereg/PREREG_NOT_BUILDABLE_SCKT_MK.md`,
commit `ecfd67f7`, before any fitting.)

Evidence (verified in payloads, `analysis/DATA_UNDERSTANDING.md`):
`content.stats` is absent (null) in all 1,022 payloads, and
`content.shotmap.shots` is an empty list in all 1,022. No total-shots
target exists in any season (2021/22–2026/27); the stats era never
starts in this league. The world-index flags agree (`has_stats`
False, `has_shotmap` False, 1,022/1,022) but were not trusted — the
absence was re-derived from the payloads.

Consequence: no total-shots model (the shots family / v1 / v2 / E9
patterns or any variant) can be built, no dev window exists, and no
virgin window exists. T-MK is NOT BUILDABLE. Nothing ships.
