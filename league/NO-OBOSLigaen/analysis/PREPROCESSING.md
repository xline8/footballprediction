# NO-OBOSLigaen preprocessing

The builder is [build_data.py](../data/build_data.py). It performs no fitting, preregistration or gate evaluation.

## Numbered rules

1. Include played matches with a score; retain header `scoreStr` as the goals target.
2. Keep rounds 1–30 as `phase=regular`; play-offs are outside league 203.
3. Key teams by FotMob team ID. Names are labels, never join keys.
4. Derive HT goals from events. `ht_source=events` for all 1,440 rows; never infer HT from absent period stats.
5. Preserve missing targets as null. Count-market scoring skips a row without its target; no target is imputed or converted to zero.
6. Preserve All-only stats and provenance flags. Half-stat columns stay null where no period feed exists.
7. Cards use one event-unified target: Yellow + YellowRed. The stats feed has no reliable cards key and no cards block in the thin early regime, so events are the complete auditable source; Red is excluded.
8. Preserve referee nulls, shotmap absence, stats-block/key gaps and the 2024 counting-regime break as provenance.
9. Sort by date and match ID. Future walk-forward consumers must use strictly pre-match windows.

## Verification

There are 1,440 match rows and 2,880 team rows; IDs are unique; events reproduce the score in 1,440/1,440 matches; awarded = 0. Mover logic is ID-keyed: entrants are current-season clubs absent from the prior OBOS season, partitioned by prior-season Eliteserien membership.
