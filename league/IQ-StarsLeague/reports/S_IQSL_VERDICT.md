# Verdict — S-IQSL (shots on target): **NOT BUILDABLE**

No prereg was written and nothing was fitted for this candidate,
because the feasibility condition in the programme template fails:
**the target does not exist in the data, in dev or in virgin.**

Evidence (Step 1, measured from payload content, not index flags):
`content.stats` is null in 2,032/2,032 payloads, so there is no
`ShotsOnTarget` key in any season. The only other SOT source, the
shotmap, is empty in 2,032/2,032 payloads (`content.shotmap.shots` is
`[]` everywhere, including the virgin season 2025/2026). The event
feed carries goals and red-card variants only — no shot events.

With no target in any season there is no gate to run and no virgin to
read. **S-IQSL is NOT BUILDABLE and nothing ships.** If FotMob
restores this league's stats/shotmap feed for a full recent season,
the candidate needs a fresh six-step pass over the new data; nothing
in this build pre-registers it.
