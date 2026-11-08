# France Ligue 2 — preprocessing

`data/build_data.py` reads the main warehouse index for league_id 110 and keeps finished matches only. The current build contains 1,859 matches and 3,718 team-match rows; CSVs are generated locally and are not committed.

- Scores come from the feed status; half-time goals come from goal events at time ≤45.
- Phase is derived from `matchRound`/`leagueRoundName`. The observed French feed contains only numeric rounds 1–38, so every built row is regular; no playoff/play-out rows are guessed.
- Stats are flattened separately for All, FirstHalf, and SecondHalf. Missing period splits remain missing.
- Both stats-feed `yellow_cards` and event-feed Yellow cards are retained, including event first-half yellows. EDA chooses the event target because the feeds differ systematically.
- Shotmap fields are regulation-only and include shots, SOT, xG, xGOT, and first-half shot counts.
- Referee is read from `content.matchFacts.infoBox.Referee.text`.
- Team identity is keyed by FotMob team_id. Ligue 1 parent is id 53; the lower-tier mover source present in the index is Ligue 3 id 8970.
