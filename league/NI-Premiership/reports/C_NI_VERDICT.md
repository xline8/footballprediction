# Verdict — C-NI (NI-Premiership corners): **NOT BUILDABLE**

No prereg exists for C-NI, no engine was built, and no virgin data
was read — there is nothing to fit.

Evidence (verified in payloads, `analysis/DATA_UNDERSTANDING.md`):
`content.stats` is absent (null) in all 1,242 payloads. No corners
target exists in any season (2021/22–2026/27); the stats era never
starts in this league. The world-index flags agree (`has_stats`
False, 1,242/1,242) but were not trusted — the absence was
re-derived from the payloads.

Consequence: no corners model (production `model_corners_v3`
pattern or any variant) can be built, no dev window exists, and no
virgin window exists. C-NI is NOT BUILDABLE. Nothing ships.
