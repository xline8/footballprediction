# Verdict — K-IQSL (cards): **NOT BUILDABLE**

No prereg was written and nothing was fitted for this candidate,
because the feasibility condition in the programme template fails:
**the target (yellow cards) does not exist in the data, in dev or in
virgin.**

Evidence (Step 1, measured from payload content, not index flags):
`content.stats` is null in 2,032/2,032 payloads, so there are no
stats-feed cards in any season. The event feed is the only other
possible source, and it carries no Yellow events at all: Card events
are Red and YellowRed only (dev-era 2024/2025: 78 Red + 2 YellowRed,
zero Yellow), and the event feed is absent entirely in 2021/2022–
2023/2024. The virgin season likewise contains zero Yellow events.
Red cards are a rare-event count (0.25 per event-bearing match in
2024/2025), not a valid cards target — the production cards design
excludes reds, and no reliability evidence exists for them.

With no yellow-card target in any season there is no gate to run and
no virgin to read. **K-IQSL is NOT BUILDABLE and nothing ships.** If
FotMob restores this league's stats feed, or starts publishing Yellow
events, for a full recent season, the candidate needs a fresh
six-step pass over the new data; nothing in this build pre-registers
it.
