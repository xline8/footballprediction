# Data understanding — IS-1Deild

The re-checked index has 812 rows for FotMob league 216, dated 2021-05-06 through 2026-09-19. Seasons are calendar-year labels. The built files contain 132, 132, 137, 137, 137 and 137 matches for 2021–2026. 2026 is complete: 132 regular matches plus five promotion-playoff matches, ending 2026-09-19.

The format is 12 teams and 22 regular rounds (132 matches). Promotion playoffs were introduced in 2023: four semi-finals (`leagueRoundName=1/2`) and one final per season. Thus 2021–2022 have no playoff rows; this is supported by the payload labels and is documented as a format change.

Coverage is score 812/812, events 790/812, stats 0/812, period splits 0/812, named referees 0/812, and shotmaps/xG 0/812. The 22 event-less match IDs are:

`3537487, 3537545, 3794954, 3795015, 4084243, 4389633, 4389639, 4389652, 4389642, 4389707, 4389718, 4389719, 4389697, 4635817, 5225739, 5225740, 5225759, 5225761, 5225796, 5225804, 5225813, 5225842`.

The exact score/event discrepancy is match `3794991`, 2022-09-03, Selfoss–Grindavik: `scoreStr=0-3`, awarded status true, while the event list contains five home and three away Goal events. The builder retains 0–3 and never repairs the event feed.

Team identity is stable by FotMob ID. The published-name variants are 4661 Throttur Reykjavik/Thróttur Reykjavík; 8299 IBV Vestmannaeyjar/ÍBV Vestmannaeyjar; 4516 HK Kopavogs/HK Kópavogs; 4495 Njardvik/Njarðvík; 6683 Leiknir Reykjavik/Leiknir Reykjavík; and 163250 IR Reykjavik/ÍR Reykjavík. The machine-readable counts and IDs are in `inventory_summary.json`.

The source check for the 2. Deild mover pool found 16 malformed payloads without `general.homeTeam` (IDs listed in the inventory). They were guarded with `.get` and do not crash the 216 builder; the 216 payloads themselves are complete.

