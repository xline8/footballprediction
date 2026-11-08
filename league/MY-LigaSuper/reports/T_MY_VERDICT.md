# Verdict — T-MY (Malaysia Liga Super total shots): **NOT BUILDABLE**

No prereg arms exist for T-MY, no engine was built, and no virgin data
was read — there is nothing to fit. (The not-buildable standing is
pre-registered in Phase A: `prereg/PREREG_NOT_BUILDABLE_SCKT_MY.md`,
commit `c3d1a0cf`, before any fitting.)

Evidence (verified in payloads, `analysis/DATA_UNDERSTANDING.md`):
`content.stats` is null in all 793 payloads and `content.shotmap.shots`
is empty in all 793. No total-shots target exists in any season
(2021–2026/2027); the stats/shotmap era never starts in this league.
The world-index flags agree (`has_stats` False, `has_shotmap` False,
793/793) but were not trusted — the absence was re-derived from the
payloads.

Consequence: no total-shots model (the shots family / v2 / E9 pattern
or any variant) can be built, no dev window exists, and no virgin
window exists. T-MY is NOT BUILDABLE. Nothing ships.
