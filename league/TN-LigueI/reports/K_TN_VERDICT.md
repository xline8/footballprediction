# Verdict — K-TN (Tunisia Ligue I cards): **NOT BUILDABLE**

No prereg exists for K-TN, no engine was built, and no virgin data
was read — there is nothing to fit.

Evidence (verified in payloads, `analysis/DATA_UNDERSTANDING.md` /
EDA.md F5):
- `content.stats` is absent (null) in all 1,060 payloads, so no
  stats-feed yellows exist in any season.
- Event cards (`matchFacts.events.events`, type `Card`) exist but
  are Red (227) and YellowRed (14) ONLY — 241 events in 216 matches
  (0.23/match), fragmentary, not a complete feed. **No plain Yellow
  event exists anywhere in the league.** The cards market is a
  total-cards (yellows + reds) line; with zero yellow data the
  target does not exist.
- Referee identity is absent: `infoBox.Referee.text` is "" in all
  1,060 payloads. Referee strictness is unmeasurable even as a
  covariate, so X8 is dropped on absence (FEATURES.md).
- Red-card counts (0.23/match, fragmentary) are a rare-event
  descriptive series with no reliability evidence and no production
  analogue as a target (J1 FEATURES.md R12). They are carried in the
  CSV as descriptive columns only.

Consequence: no cards model (production `model_cards.py` pattern
or referee arm) can be built, no dev window exists, and no virgin
window exists. K-TN is NOT BUILDABLE. Nothing ships.
