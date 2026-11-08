# Phase A — Preprocessing: SCO Championship

Only played matches in the supplied CSV are included. Every included row is `phase=regular`; this is frozen because the feed contains no play-off rows.

Goals use the full-time home and away goal fields. First-half goals and cards halves are sourced from the event feed. The cards target is the total of event yellow cards (`ev_yellow_home + ev_yellow_away`) for every match. On the 19 rich matches where stats `yellow_cards` is also present, it agrees exactly with event yellows, so there is no source-mixing risk; the event target is used for the whole corpus because the stats key is absent in the other 950 matches.

Stats-market rows are those with `has_stats_all=1`; target values require both home and away values for the relevant key. No period-stat values are used for SOT, corners, or total shots. Period fields are used only where the event reconstruction supplies first-half goals/cards.

All team joins and historical aggregates use numeric team IDs. Display-name changes, including ID 8066’s Inverness naming variation, are not treated as new teams. Features are strictly pre-match trailing/expanding quantities; missing observations remain missing and are never imputed in this phase.
