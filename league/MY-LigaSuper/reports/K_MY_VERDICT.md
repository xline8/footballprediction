# Verdict — K-MY (Malaysia Liga Super cards): **NOT BUILDABLE**

No prereg arms exist for K-MY, no engine was built, and no virgin data
was read — there is nothing to fit. (The not-buildable standing is
pre-registered in Phase A: `prereg/PREREG_NOT_BUILDABLE_SCKT_MY.md`,
commit `c3d1a0cf`, before any fitting.)

Evidence (verified in payloads, `analysis/DATA_UNDERSTANDING.md`):
card events total 127 across 793 matches — Red 88, YellowRed 39, and
plain Yellow 0. There is no yellow-card target in any season, and the
referee is never named (`infoBox.Referee.text` empty in 793/793), so
no referee feature exists either. The event feed's card coverage is
plainly incomplete (0.16 card events per match), not a usable target.

Consequence: no cards model (production `model_cards` pattern or any
variant, with or without a referee arm) can be built, no dev window
exists, and no virgin window exists. K-MY is NOT BUILDABLE. Nothing
ships.
