# Phase 1 — Data Understanding: Poland II Liga

The FotMob 8935 index has 1,679 rows: 309 in each complete season
2021/2022–2025/2026 and 134 in 2026/2027 through 2026-11-08. The builder
produces 1,679 unique matches, 3,358 team rows, and 47 FotMob team IDs.
FT scores parse from `header.status.scoreStr`; parentLeagueId is 8935 and
coverageLevel is lower throughout.

This is scores-only. Payload assertions find `content.stats` null and an
empty `content.shotmap.shots` in 1,679/1,679 rows. No referee, period
split, SOT, corners, cards, total shots, or xG target exists.

Each complete season has 18 teams, 306 regular matches, and three
promotion-playoff matches. In 2021/2022, raw names are `2. Division` 196,
`II Liga` 110, and the promotion playoff 3. The rename from `2. Division`
to `II Liga` falls mid-season (`2. Division` 2021-07-30 → 2022-03-09,
`II Liga` from 2022-02-26); both names are the same regular season. The frozen mapping is the
first two names to `regular`, and the last to `playoff_promotion`; all rows
are ordinary in fits and no phase feature is used.

Goal events are present in 1,537 rows and validate in 1,536. The sole
mismatch is 4202068 (ŁKS Łódź II 0–3 Polonia Bytom, awarded). There are
142 no-event rows: 120 are 0–0 and 22 are 3–0/0–3 walkovers; 26 rows in
total are awarded (23 scored 3–0/0–3, 3 are 0–0). Complete
validated half rows are 1,522; the frozen 1H share is 1,802/4,220 = 0.4270.
The event feed carries no plain-Yellow card events at all: 365 Card
events in 1,679 matches are 173 Red + 192 YellowRed only, so the
`ev_yellow_*` columns are 0 by feed construction and there is no
yellow-card target anywhere in the corpus. The 2022/2023 playoff final
was 1–1 and decided on penalties (FT score stands); the only goal-event
times past 90' are extra-time goals at 116' and 118' in playoff matches.

Team identity is FotMob ID. B teams are ordinary rows; the frozen IDs are
585552, 585484, 556984, 1501585, and 585596. B-team appearances are 409
in 391 complete-season matches (25.3%): B teams score 1.315 and concede
1.592 per appearance, against 1.399/1.357 for non-B teams (gaps −0.085 /
+0.192); B-involved matches average 2.877 goals vs 2.742 without a B team.
Newcomer origin is checked
from prior-season I Liga payload membership (league 197). Dev gaps are
I-Liga-relegated n=9, −0.057 GF/−0.060 GA, and from-below n=12,
+0.113 GF/−0.023 GA; all-complete gaps are relegated n=11, −0.017/−0.100,
and from-below n=17, +0.137/−0.041. See `eda_numbers.json` for the source calculations.

Observed same-ID display-name variants are: 273750 Pogon Siedlce/Pogoń
Siedlce; 2415 Olimpia Elblag/ZKS Olimpia Elbląg; 1268987 Radunia
Stezyca/Radunia Stężyca; 585552 Lech Poznan ll/Lech Poznań ll; 89469 Znicz
Pruszkow/Znicz Pruszków; 585484 Slask Wroclaw ll/Śląsk Wrocław ll; 585624
Hutnik Krakow/Hutnik Kraków; 556984 Zaglebie II Lubin/Zagłębie Lubin II;
89465 GKS Jastrzebie/GKS Jastrzębie; 160406 Kotwica Kolobrzeg/Kotwica
Kołobrzeg; 2183 Polonia Warsaw/Polonia Warszawa; 1501585 LKS Lodz II/ŁKS
Łódź II; 177358 Olimpia Grudziadz/Olimpia Grudziądz; 160419 Sandecja Nowy
Sacz/Sandecja Nowy Sącz; 585211 SKRA Czestochowa/SKRA Częstochowa;
585212 Rekord Bielsko-Biala/Rekord Bielsko-Biała; 585524 Sokol
Kleczew/Sokół Kleczew; 1174006 Lechia Zielona Gora/Lechia Zielona Góra;
585611 Avia Swidnik/Avia Świdnik.
