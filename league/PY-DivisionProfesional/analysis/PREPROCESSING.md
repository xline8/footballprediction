# Step 2 — Preprocessing: PY-DivisionProfesional

Builder: `league/PY-DivisionProfesional/data/build_data.py` (regenerates
`py_matches.csv`, 1,480 rows, + `py_team_matches.csv`, 2,960 rows; CSVs
gitignored by repo norm, builder committed).

Rules (J.League preprocessing spirit, adapted):

1. **Played matches only** — `header.status.finished`; the index for
   league 199 contains only played matches (assert n = 1,480 passes).
2. **FT score** from `header.status.scoreStr`. HT goals derived from
   goal events (minute ≤ 45), flagged `ht_source = events/none`; never
   fabricated where events are absent.
3. **Stats** from `content.stats.Periods` (All / FirstHalf /
   SecondHalf), keyed by stat `key`; values parsed numerically
   (percent strings stripped). Period splits are taken only where the
   feed carries them (2025+); earlier seasons keep NaN — never filled.
4. **Cards, two provenances kept side by side**: stats-feed
   `yellow_cards_*` and event-derived `ev_yellow_*` /
   `ev_yellow_inc2nd_*` (YellowRed counts as one extra yellow).
   **The modelling target is the event-unified column** — decision and
   dev-era evidence in DATA_UNDERSTANDING.md (stats feed undercounts
   in every dev season). This was frozen before any fitting.
5. **Team identity = team_id**; display names canonicalised to the
   id's most frequent spelling (four clubs have era-varying spellings).
6. **Phase flag**: `phase = apertura/clausura` from the season label;
   the season label itself is kept verbatim as the block key. All
   tournaments are regular double round-robins — no phase exclusion
   needed (no playoff rows exist in the corpus).
7. **Referee** from `matchFacts.infoBox.Referee.text`, empty string
   where unnamed.
8. Shotmap is empty league-wide; no shotmap aggregates are written
   (nothing to aggregate — **no xG columns exist in this league's CSV**).
9. Inclusion for count-market scoring is per-match target presence:
   a match whose target columns are NaN (the 2026-04-19 clásico for
   S/C/T; also cards, its events are absent too) feeds state only
   where its own inputs exist and is never a scored row for that market.
