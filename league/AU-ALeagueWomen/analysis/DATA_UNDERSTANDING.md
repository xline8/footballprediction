# AU A-League Women — data understanding

FotMob league 9495 contains 597 finished matches: 74, 103, 139, 145, 117 and 19 by warehouse season from 2021/2022 through 2026/2027. The regular/finals split is 70/4, 99/4, 132/7, 138/7, 110/7 and 19/0. The regular season is the modelling population; finals/play-off ties are retained only for inventory and are excluded everywhere downstream.

The corpus has 10, 11, 12, 12, 11 and 11 teams. There is no promotion/relegation transition; new clubs are expansion clubs. Team identity is always `general.homeTeam.id` / `awayTeam.id`, with names retained for audit. The calendar is the southern-hemisphere season label supplied by the warehouse.

`content.stats.Periods.All` supplies total shots, shots on target, corners, yellow cards, red cards, box touches, big chances and possession essentially everywhere. Box touches is absent in two 2022/2023 matches. FirstHalf/SecondHalf splits are 0/74, 9/103, 138/139, 144/145, 117/117 and 19/19. xG and non-empty shotmaps occur only in 2025/2026 (117) and 2026/2027 (19).

Deviation found during the mandated recomputation: the `infoBox.Referee` object/key is present in 574/597 rows (the coordinator's stated 74, 103, 139, 145, 94, 19 coverage), but its `text` identity is non-empty in only 550/597 rows. The builder preserves the text value and treats blank text as missing; usable non-empty-name development coverage is 416/439. This is the identity coverage used for X8 and is reported rather than imputed.

The cards artefact is material: stats yellow totals agree with event Yellow/YellowRed totals in only 10/74, 9/103, 12/139 and 30/145 development-era matches, versus 105/117 in 2025/2026 and 19/19 in 2026/2027. Red totals agree in 596/597. Production therefore uses stats-feed yellow_cards and never event yellows for the target.
