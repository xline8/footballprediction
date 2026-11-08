# Verdict — S-NI (NI-Premiership shots on target): **NOT BUILDABLE**

No prereg exists for S-NI, no engine was built, and no virgin data
was read — there is nothing to fit.

Evidence (verified in payloads, `analysis/DATA_UNDERSTANDING.md`):
`content.stats` is absent (null) in all 1,242 payloads, and
`content.shotmap.shots` is an empty list in all 1,242. No SOT target
exists in any season (2021/22–2026/27); the stats era never starts
in this league. The world-index flags agree (`has_stats` False,
`has_shotmap` False, 1,242/1,242) but were not trusted — the absence
was re-derived from the payloads.

Consequence: no SOT model (production `model_sot.py` v5 pattern or
any variant) can be built, no dev window exists, and no virgin
window exists. S-NI is NOT BUILDABLE. Nothing ships.
