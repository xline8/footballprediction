# Preprocessing — HU-NBII

The analysis CSV contains only a genuine final score: `header.status.finished`
must be true and `header.status.scoreStr` must be non-empty. A missing score is
not treated as 0-0. A score with `finished=false` is a partial live capture and
is excluded. The builder asserts 103 missing-score exclusions and 41 partial
exclusions; it writes 200 rows.

`scoreStr` is parsed as the final home-away score. The outcome and over/BTTS
fields are derived from it. Goal events are used only for the descriptive
first-half split. A `Half` event is the required boundary. If no boundary is
present, first-half fields are NULL for non-zero matches; genuine 0-0 matches
are recorded as 0/0. Shootout events are excluded from goal-event counts.

Team names are canonicalized with NFKD ASCII folding. The script keeps an
explicit raw-spelling map for Csákvár, Zugló, Gyirmót, Kecskeméti, Kozármisleny,
Mezőkövesd, Soroksár, Szeged-Csanád, Szentlőrinc, Tiszakécske, and Fehérvár
variants. No partial or missing-score row is written.

No fitting, engine, prediction, or virgin evaluation is performed.
