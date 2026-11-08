# Verdict — K-RL2 (RO-LigaII cards)

**NOT BUILDABLE. No fitting was performed; the virgin was not read.**

Era evidence (coordinator-verified from all 1,513 warehouse payloads,
not the index flags; see analysis/DATA_UNDERSTANDING.md): there is no
yellow-card target anywhere. `content.stats` is None in all 1,513
payloads (0/1,513), and the event feed contains zero straight-Yellow
events in 1,513 matches — only Red (148) and YellowRed (106) events,
which are rare non-target audit counts, not a yellow-card target. The
referee text is blank in all 1,513 payloads, so no referee feature
exists either. There is no season — dev or virgin — in which the cards
target is observed.

A candidate needs a scorable dev window AND a virgin window containing
the target; here the target exists nowhere, so the candidate is recorded
NOT BUILDABLE rather than forced. Halves: no cards halves source exists
— frozen FT-only (no cards constant in config.yaml).

A future preregistration becomes possible only if FotMob starts
publishing stats coverage (or a complete yellow-card event feed) for
this league and a second complete covered season then exists.
