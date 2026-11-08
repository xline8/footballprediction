# Verdict — T-SLO (Slovenia Prva Liga total shots): **NOT BUILDABLE**

No prereg arms exist for T-SLO, no engine was built, and no virgin data
was read — there is nothing to fit. (The not-buildable standing is
pre-registered in Phase A: `prereg/PREREG_NOT_BUILDABLE_SCKT_SLO.md`,
commit `d973cfe6`, before any fitting.)

Evidence (verified in payloads, `analysis/DATA_UNDERSTANDING.md`):
`content.stats` is null in all 956 payloads and `content.shotmap.shots`
is empty in all 956. No total-shots target exists in any season
(2021/22–2026/27); the stats era never starts in this league. The
world-index flag agrees (`has_stats` False, 956/956) but was not
trusted — the absence was re-derived from the payloads.

Consequence: no total-shots model (the shots family pattern or any
variant) can be built, no dev window exists, and no virgin window
exists. T-SLO is NOT BUILDABLE. Nothing ships.
