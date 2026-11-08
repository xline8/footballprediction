# Verdict — S-RL2 (RO-LigaII shots on target)

**NOT BUILDABLE. No fitting was performed; the virgin was not read.**

Era evidence (coordinator-verified from all 1,513 warehouse payloads,
not the index flags; see analysis/DATA_UNDERSTANDING.md):
`content.stats` is None in all 1,513 payloads (0/1,513) and the shotmap
holds 0 shots in all 1,513 payloads, in every season including the
virgin 2025/2026. There is no season — dev or virgin — in which the
shots-on-target target is observed.

A candidate needs a scorable dev window AND a virgin window containing
the target; here the target exists nowhere, so the candidate is recorded
NOT BUILDABLE rather than forced. Halves: no SOT halves source exists —
frozen FT-only (no SOT constant in config.yaml).

A future preregistration becomes possible only if FotMob starts
publishing stats/shotmap coverage for this league and a second complete
covered season then exists.
