# Data understanding — IS-2Deild

The source is the FotMob world warehouse, league id 10226. The index has 792 rows for calendar seasons 2021–2026; 16 2021 rows are `error=true` Data not found placeholders and are never-played. The analysis corpus is 776 finished matches: 116 in 2021 and 132 in each of 2022–2026.

Every played payload has an official score, but `content.stats` is `None`, `content.shotmap.shots` is empty, and the referee text is empty. Goal events are in `header.events` and total 2,811, exactly matching the sum of FT scores. There are 145 Card events, too sparse for a target. First-half goals are derivable only from goal-event times; there is no stats period split.

Each season is a 12-team, 22-round, six-match-per-round plain double round robin with no split or playoff phase. Seasons are calendar years. The 2026 season is complete through 2026-09-12. Identity is keyed by FotMob id: id 163250 appears as IR Reykjavik and ÍR Reykjavík, and id 4515 as Vikingur Olafsvik and Víkingur Olafsvik. The 2026 Magni–KFG schedule has Magni at home twice; both matches are retained as played.
