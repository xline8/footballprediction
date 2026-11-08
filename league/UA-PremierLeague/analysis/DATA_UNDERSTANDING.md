# Step 1 — Data Understanding: Ukraine Premier League (FotMob 441)

Corpus: 1,191 index rows, seasons 2021/2022–2026/2027 (split-year).
Per-season: 2021/2022 n=143 (rounds 1–18 only), 2022/2023–2025/2026
n=240 each (16 teams, 30 rounds, single double round-robin),
2026/2027 n=88 (in progress at warehouse pull, through 2026-11-08).

FORMAT: no championship/relegation groups exist in the warehouse era
— every season is one group, rounds 1–30, phase = regular for all
rows. (Pre-2021 UPL split formats are outside the corpus.) Team
count by id is 16 in every season (name count reads 17–18 only
because of spelling variants, below).

COVERAGE (from eda_numbers.json): score 1,191/1,191; events
1,191/1,191; stats (Periods.All with corners key) 1,179/1,191 but
22 of those are all-zero stubs (see PREPROCESSING stub rule) →
valid stats rows 1,157. Period splits: NONE in any match
(has_period_splits 0/1,191). Shotmap: empty everywhere (0 shots).
xG (`expected_goals`), set-play xG, `big_chance`, `touches_opp_box`:
absent in 1,191/1,191 payloads. Stats feed carries ONLY
BallPossesion, total_shots, ShotsOnTarget, corners. Stats
`yellow_cards` key: absent in 1,191/1,191 payloads — cards exist
ONLY in the event feed. Referee (`infoBox.Referee.text`): empty in
1,191/1,191 payloads.

WAR-ERA FACTS (checked on the corpus, frozen treatment in
PREPROCESSING/MODEL_DESIGN): the 2021/2022 season stops on
2021-12-12 after round 18 (143 of 240 fixtures) — the season was
terminated after the February 2022 invasion and never completed;
no cancelled/abandoned flags appear in the warehouse (cancelled=0,
not_finished=0), the termination shows purely as truncation.
2022/2023 starts late (2022-08-23). Clubs present in 2021/2022 and
never again: Mariupol (6657), Desna, FC Lviv, Metalist Kharkiv —
dissolved or dropped out after the invasion. Home-win rate fell to
0.388–0.400 in 2022/2023–2024/2025 vs 0.441 in the partial
2021/2022 — consistent with displaced/neutral-venue home fixtures,
recorded as context, not modelled. Air-raid interruptions are not
encoded in the feed and cannot be modelled.

TEAM IDENTITY: 27 distinct team ids; names are NOT stable — id 6072
appears as "FC Oleksandriya"/"FC Olexandriya", id 8666 as
"Chornomorets Odesa"/"Chornomorets Odessa", id 949030 as
"Metalist 1925"/"FC Kharkiv" (rename). No name maps to two ids.
ALL logic keys on team ids.

LEVELS (per match): goals 2.66 (2021/22 partial), 2.45, 2.49, 2.25,
2.57, 2.36 (2026/27 partial). SOT 7.87, 6.33, 7.09, 5.77, 7.21,
6.62. Corners 9.12, 9.29, 9.09, 8.21, 9.43, 8.69. Total shots
16.62, 14.43, 15.17, 12.39, 15.27, 16.22 — far below European
norms (~25): this feed's shot counting is thin, and the 2024/2025
dip (shots −18%, SOT −19% vs neighbours, rebounding in 2025/2026)
is a feed-level instability, documented here; the gates, not window
surgery, decide what it means. Event yellows: 5.15, 4.69, 4.64,
3.95, 3.65, 4.14 per match — a falling level across the era.
