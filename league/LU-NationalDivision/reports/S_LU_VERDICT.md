# Verdict — S-LU (LU-NationalDivision shots on target): **NOT BUILDABLE**

No prereg exists for S-LU, no engine was built, and no virgin data
was read — there is nothing to fit.

Evidence (verified in payloads, `analysis/DATA_UNDERSTANDING.md`):
`content.stats` is absent (null) in all 1,296 payloads and
`content.shotmap.shots` is an empty list in all 1,296. No SOT
target exists in any season (2021/22–2026/27); the stats era never
starts in this league. The world-index flags agree
(`has_stats`/`has_shotmap` False, 1,296/1,296) but were not trusted
— the absence was re-derived from the payloads, including the
key-present-but-empty shotmap case.

Consequence: no S-J1-style model (v5 Poisson ridge + Negative
Binomial + Beta-Binomial on-target ratio) can be built, no dev
window exists, and no virgin window exists. S-LU is NOT BUILDABLE.
Nothing ships.
