# Verdict — K-LU (LU-NationalDivision cards): **NOT BUILDABLE**

No prereg exists for K-LU, no engine was built, and no virgin data
was read — there is nothing to fit.

Evidence (verified in payloads, `analysis/DATA_UNDERSTANDING.md` /
EDA.md F5):
- `content.stats` is absent (null) in all 1,296 payloads, so no
  stats-feed yellows exist in any season.
- Event cards (`matchFacts.events.events`, type `Card`) exist but
  are Red (232) and YellowRed (153) ONLY — 385 events, 0.30/match.
  **No plain Yellow event exists anywhere in the league.** The
  cards market is a total-cards (yellows + reds) line; with zero
  yellow data the target does not exist.
- Referee identity is absent in content: `infoBox.Referee.text` is
  `""` in all 1,296 payloads (key present, content empty). Referee
  strictness is unmeasurable even as a covariate, so X8 is dropped
  on absence (FEATURES.md).
- Red-card counts (0.30/match) are a rare-event descriptive series
  with no reliability evidence and no production analogue as a
  target (J1 FEATURES.md R12). They are carried in the CSV as
  descriptive columns only.

Consequence: no cards model (production `model_cards.py` pattern
or referee arm) can be built, no dev window exists, and no virgin
window exists. K-LU is NOT BUILDABLE. Nothing ships.
