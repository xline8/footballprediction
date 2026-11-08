# Verdict — S-CLA (Chile Liga de Ascenso shots on target) — **NOT BUILDABLE**

No prereg was written and nothing was fitted (TH-ThaiLeague2 /
ID-SuperLeague precedent for not-buildable candidates).

Era evidence (computed from payload content, not index flags —
`analysis/DATA_UNDERSTANDING.md`): the index flags `has_stats` on
483 payloads (250 in 2025, 233 in 2026), but the stats block is an
empty shell in every one: `content.stats` is `None` in all
2021–2024 payloads and `{"Periods": {"All": null}}` in all 483
flagged payloads. **Zero of 1,515 matches carry a single stat
value**; `ShotsOnTarget` therefore exists in no season — no
scorable dev window and no virgin window contain the target.
The shotmap is an empty list in every payload as well, so no
alternative SOT source exists.

A market whose target verifiably exists nowhere is not forced.
S-CLA = NOT BUILDABLE. If a future warehouse refresh populates
the stats block, feasibility must be re-mapped from payload
content before any prereg is written.
