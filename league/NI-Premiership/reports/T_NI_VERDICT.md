# Verdict — T-NI (NI-Premiership total shots): **NOT BUILDABLE**

No prereg exists for T-NI, no engine was built, and no virgin data
was read — there is nothing to fit.

Evidence (verified in payloads, `analysis/DATA_UNDERSTANDING.md`):
`content.stats` is absent (null) in all 1,242 payloads, and
`content.shotmap.shots` is an empty list in all 1,242. No total-shots
target exists in any season (2021/22–2026/27); the stats era never
starts in this league. The world-index flags agree (`has_stats`
False, `has_shotmap` False, 1,242/1,242) but were not trusted — the
absence was re-derived from the payloads.

Consequence: no total-shots model (the shots family in
`experiments/` or the J1 total-shots engine pattern) can be built, no
dev window exists, and no virgin window exists. T-NI is NOT
BUILDABLE. Nothing ships.
