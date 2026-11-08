# Verdict — S-MY (Malaysia Liga Super shots on target): **NOT BUILDABLE**

No prereg arms exist for S-MY, no engine was built, and no virgin data
was read — there is nothing to fit. (The not-buildable standing is
pre-registered in Phase A: `prereg/PREREG_NOT_BUILDABLE_SCKT_MY.md`,
commit `c3d1a0cf`, before any fitting.)

Evidence (verified in payloads, `analysis/DATA_UNDERSTANDING.md`):
`content.stats` is null in all 793 payloads and `content.shotmap.shots`
is empty in all 793. No SOT target exists in any season (2021–
2026/2027); the stats era never starts in this league. The world-index
flags agree (`has_stats` False, `has_shotmap` False, 793/793) but were
not trusted — the absence was re-derived from the payloads.

Consequence: no SOT model (production `model_sot` v5 pattern or any
variant) can be built, no dev window exists, and no virgin window
exists. S-MY is NOT BUILDABLE. Nothing ships.
