# Preprocessing — Wales Cymru Premier

`data/build_data.py` reads the main-repo index and each payload path, writes one row per index row to `wal_matches.csv`, and writes one row per team-match for eligible rows to `wal_team_matches.csv`.

Rules are frozen: retain all 1,103 finished rows; use payload `scoreStr`; exclude only playoff stages (`eligible=0`); classify stage from `Tournament.leagueName`; retain split rows as ordinary pooled rows; preserve season labels and string playoff rounds; key teams by ID; use general names as displayed. HT is Half@45 when present, otherwise only eventless 0–0 receives `implied_0_0`; no other HT is fabricated. No stats, shotmap, lineup, referee or target imputation occurs.

Assertions are 1,103 rows, 1,087 eligible, 16 playoffs, 2,174 eligible team rows, and 1,103/1,103 goal-event score agreement. The AET and penalty rows remain audit rows and never enter EDA/model data.
