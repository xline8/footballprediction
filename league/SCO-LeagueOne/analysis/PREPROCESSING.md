# Phase A — Preprocessing: SCO League One

All 969 supplied rows are played matches and all are frozen as `phase=regular`; no play-off rows are present. Full-time goals come from the payload score and reconcile with event goals for 969/969 matches.

Team joins and historical aggregates use FotMob team IDs. Display names are labels only; ID 4130’s “Edinburgh City” / “FC Edinburgh” alias is not a new club.

First-half goals are event goals with `time <= 45`, excluding penalty-shootout events. First-half cards are event `Yellow` cards with `time <= 45`; the K target is total event Yellow cards, with a separate descriptive Yellow+YellowRed series. Red-event counts include Red and YellowRed. Stats-derived `yellow_*` fields use the reference stats-to-events fallback, but the stats columns are all `None` by construction because no payload has stats Periods content. No xG, SOT, corners, total-shots, shotmap, or referee values are invented.

The builder reads payloads read-only from the main warehouse checkout, exactly by index path. Generated CSVs are extraction artefacts; no fitting or imputation occurs in Phase A.
