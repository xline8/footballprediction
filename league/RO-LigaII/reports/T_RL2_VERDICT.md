# Verdict — T-RL2 (RO-LigaII total shots)

**NOT BUILDABLE. No fitting was performed; the virgin was not read.**

Era evidence (coordinator-verified from all 1,513 warehouse payloads,
not the index flags; see analysis/DATA_UNDERSTANDING.md): the total
shots target exists only where the FotMob stats feed (`total_shots`)
or the shotmap exists, and `content.stats` is None in all 1,513
payloads (0/1,513) while the shotmap is empty in all 1,513 payloads,
in every season including the virgin 2025/2026. There is no season —
dev or virgin — in which the target is observed.

A candidate needs a scorable dev window AND a virgin window containing
the target; here the target exists nowhere, so the candidate is recorded
NOT BUILDABLE rather than forced. Halves: no total-shots halves source
exists — frozen FT-only (no shots constant in config.yaml).

A future preregistration becomes possible only if FotMob starts
publishing stats/shotmap coverage for this league and a second complete
covered season then exists.
