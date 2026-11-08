# Verdict — K-SLO (Slovenia Prva Liga cards/yellows): **NOT BUILDABLE**

No prereg arms exist for K-SLO, no engine was built, and no virgin data
was read — there is nothing to fit. (The not-buildable standing is
pre-registered in Phase A: `prereg/PREREG_NOT_BUILDABLE_SCKT_SLO.md`,
commit `d973cfe6`, before any fitting.)

Evidence (verified in payloads, `analysis/DATA_UNDERSTANDING.md`): the
event feed contains 176 Card events across 956 payloads — 125 Red and
51 YellowRed — and ZERO plain Yellow events. Referee text is empty in
956/956 payloads, so no referee feature exists either. The red-family
events that do exist are not a yellow-cards target and were not used as
a covariate.

Consequence: no cards model (production `model_cards` pattern or any
variant) can be built, no dev window exists, and no virgin window
exists. K-SLO is NOT BUILDABLE. Nothing ships.
