# Verdict — C-CLA (Chile Liga de Ascenso corners) — **NOT BUILDABLE**

No prereg was written and nothing was fitted (TH-ThaiLeague2 /
ID-SuperLeague precedent for not-buildable candidates).

Era evidence (computed from payload content, not index flags —
`analysis/DATA_UNDERSTANDING.md`): the index flags `has_stats` on
483 payloads (250 in 2025, 233 in 2026), but the stats block is an
empty shell in every one: `content.stats` is `None` in all
2021–2024 payloads and `{"Periods": {"All": null}}` in all 483
flagged payloads. **Zero of 1,515 matches carry a single stat
value**; the `corners` key therefore exists in no season — no
scorable dev window and no virgin window contain the target.
No period splits exist either, so there is no halves source.

A market whose target verifiably exists nowhere is not forced.
C-CLA = NOT BUILDABLE. If a future warehouse refresh populates
the stats block, feasibility must be re-mapped from payload
content before any prereg is written.
