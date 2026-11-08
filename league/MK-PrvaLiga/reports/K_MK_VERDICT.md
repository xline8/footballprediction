# Verdict — K-MK (North Macedonia Prva Liga cards): **NOT BUILDABLE**

No prereg arms exist for K-MK, no engine was built, and no virgin data
was read — there is nothing to fit. (The not-buildable standing is
pre-registered in Phase A: `prereg/PREREG_NOT_BUILDABLE_SCKT_MK.md`,
commit `ecfd67f7`, before any fitting.)

Evidence (verified in payloads, `analysis/DATA_UNDERSTANDING.md` /
EDA.md F5):
- `content.stats` is absent (null) in all 1,022 payloads, so no
  stats-feed yellows exist in any season.
- Event cards (`matchFacts.events.events`, type `Card`) exist but
  are Red (131) and YellowRed (87) ONLY — 218 events in 185 matches.
  **No plain Yellow event exists anywhere in the league.** The cards
  market is a total-cards (yellows + reds) line; with zero yellow
  data the target does not exist.
- Referee identity is absent: `infoBox.Referee.text` is "" in all
  1,022 payloads. Referee strictness is unmeasurable even as a
  covariate, so X8 is dropped on absence (FEATURES.md).
- Red-card counts (131 Red + 87 YellowRed, fragmentary) are a
  rare-event descriptive series with no reliability evidence and no
  production analogue as a target (J1 FEATURES.md R12). They are
  carried in the CSV as descriptive columns only.

Consequence: no cards model (production `model_cards.py` pattern
or referee arm) can be built, no dev window exists, and no virgin
window exists. K-MK is NOT BUILDABLE. Nothing ships.
