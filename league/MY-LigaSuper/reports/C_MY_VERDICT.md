# Verdict — C-MY (Malaysia Liga Super corners): **NOT BUILDABLE**

No prereg arms exist for C-MY, no engine was built, and no virgin data
was read — there is nothing to fit. (The not-buildable standing is
pre-registered in Phase A: `prereg/PREREG_NOT_BUILDABLE_SCKT_MY.md`,
commit `c3d1a0cf`, before any fitting.)

Evidence (verified in payloads, `analysis/DATA_UNDERSTANDING.md`):
`content.stats` is null in all 793 payloads. No corner target exists
in any season (2021–2026/2027); the stats era never starts in this
league. The world-index flag agrees (`has_stats` False, 793/793) but
was not trusted — the absence was re-derived from the payloads.

Consequence: no corners model (production `model_corners_v3` pattern
or any variant) can be built, no dev window exists, and no virgin
window exists. C-MY is NOT BUILDABLE. Nothing ships.
