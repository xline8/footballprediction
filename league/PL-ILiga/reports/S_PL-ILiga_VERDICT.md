# Verdict — S-PL-ILiga (Poland I Liga shots on target)

**NOT BUILDABLE. No fitting was performed; the virgin was not read.**

Era evidence (coordinator-verified from the warehouse index and a full
1,671-file payload scan; see analysis/DATA_UNDERSTANDING.md): the
ShotsOnTarget target exists only where the FotMob stats feed exists,
and `content.stats` is None in all 1,671 I Liga payloads (0/1,671),
in every season including the virgin 2025/2026. The shotmap is likewise
empty in all 1,671 payloads, so no shotmap-derived SOT exists either.
There is no season — dev or virgin — in which the target is observed.

A candidate needs a scorable dev window AND a virgin window containing
the target; here the target exists nowhere, so the candidate is recorded
NOT BUILDABLE rather than forced. Halves: no SOT halves source exists —
frozen FT-only (no SOT constant in config.yaml).

A future preregistration becomes possible only if FotMob starts
publishing stats/shotmap coverage for this league and a second complete
covered season then exists.
