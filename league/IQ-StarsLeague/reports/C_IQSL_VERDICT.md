# Verdict — C-IQSL (corners): **NOT BUILDABLE**

No prereg was written and nothing was fitted for this candidate,
because the feasibility condition in the programme template fails:
**the target does not exist in the data, in dev or in virgin.**

Evidence (Step 1, measured from payload content, not index flags):
`content.stats` is null in 2,032/2,032 payloads, so there is no
`corners` key in any season. There is no other corners source in the
payload: the shotmap is empty in 2,032/2,032 payloads, and the event
feed carries goals and red-card variants only — no corner events.

With no target in any season there is no gate to run and no virgin to
read. **C-IQSL is NOT BUILDABLE and nothing ships.** If FotMob
restores this league's stats feed for a full recent season, the
candidate needs a fresh six-step pass over the new data; nothing in
this build pre-registers it.
