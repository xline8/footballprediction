# Verdict — C_BEB (BE-FirstDivisionB corners)

**NOT BUILDABLE. No fitting was performed; the virgin was not read.**

Era evidence (coordinator-verified from the warehouse index and a
full 1,114-file payload scan; see analysis/DATA_UNDERSTANDING.md):
the corners target exists only where the FotMob stats feed exists —
2025/2026 (277/278 matches), which is this build's VIRGIN season,
and the partial 2026/2027 (70/70), which is reserved confirmatory.
The entire dev era (2021/2022–2024/2025, 766 matches) carries ZERO
stats rows. A candidate needs a scorable dev window AND a virgin
window containing the target; here the target's era lies entirely
inside the virgin, leaving no dev window. Fitting on the virgin
would burn the only clean read and is forbidden by the program's
gate discipline, so the candidate is recorded NOT BUILDABLE rather
than forced.

Descriptive level, 2025/2026 only (public feed fact, no model):
corners = 9.6029 per match. Halves: no legitimate halves source exists in
any dev window for this market — frozen FT-only (halves share null
in config.yaml).

A future preregistration becomes possible once a second complete
stats-era season exists (dev on 2025/2026, virgin on the completed
2026/2027 or later).
