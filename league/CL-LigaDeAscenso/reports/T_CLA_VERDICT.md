# Verdict — T-CLA (Chile Liga de Ascenso total shots) — **NOT BUILDABLE**

No prereg was written and nothing was fitted (TH-ThaiLeague2 /
ID-SuperLeague precedent for not-buildable candidates).

Era evidence (computed from payload content, not index flags —
`analysis/DATA_UNDERSTANDING.md`): the index flags `has_stats` on
483 payloads (250 in 2025, 233 in 2026), but the stats block is an
empty shell in every one: `content.stats` is `None` in all
2021–2024 payloads and `{"Periods": {"All": null}}` in all 483
flagged payloads. **Zero of 1,515 matches carry a single stat
value**; `total_shots` therefore exists in no season, and the
shotmap is an empty list in every payload, so neither the stats
target nor a shotmap-derived target exists in any window —
dev or virgin.

A market whose target verifiably exists nowhere is not forced.
T-CLA = NOT BUILDABLE. If a future warehouse refresh populates
the stats block, feasibility must be re-mapped from payload
content before any prereg is written.
