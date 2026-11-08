# Verdict — S-MK (North Macedonia Prva Liga shots on target): **NOT BUILDABLE**

No prereg arms exist for S-MK, no engine was built, and no virgin data
was read — there is nothing to fit. (The not-buildable standing is
pre-registered in Phase A: `prereg/PREREG_NOT_BUILDABLE_SCKT_MK.md`,
commit `ecfd67f7`, before any fitting.)

Evidence (verified in payloads, `analysis/DATA_UNDERSTANDING.md`):
`content.stats` is absent (null) in all 1,022 payloads, and
`content.shotmap.shots` is an empty list in all 1,022. No SOT target
exists in any season (2021/22–2026/27); the stats era never starts
in this league. The world-index flags agree (`has_stats` False,
`has_shotmap` False, 1,022/1,022) but were not trusted — the absence
was re-derived from the payloads.

Consequence: no SOT model (production `model_sot.py` v5 pattern or
any variant) can be built, no dev window exists, and no virgin
window exists. S-MK is NOT BUILDABLE. Nothing ships.
