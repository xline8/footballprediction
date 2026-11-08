# TR-1Lig feature decisions

| feature | decision | league-specific reason |
|---|---|---|
| X1 xG blend | ADOPTED as goals-only fallback | xG is absent before the 2024/25 fragment; goals-only is the norm and any blend is nearly inert in dev. |
| X2 mover | ADOPTED as arm candidate | 26 measurable SüperLig↔1.Lig transitions: 14 downward, 12 upward; mean GF/GA shifts are in `eda_numbers.json`. Two-Lig promotions are not in the parent corpus and use Gate Zero unseen-team treatment. |
| X3 set-play | DROPPED | no usable virgin shotmap/stats arm; fragment-only evidence cannot form dev + virgin. |
| X4 shotmap | DROPPED | shotmap exists only in the 2024/25 fragment and is zero in virgin 2025/26. |
| X5 trailing target means | DROPPED for count candidates | only stats-era and not fillable across the season-blocked count dev window. |
| X6 xGOT | DROPPED | shotmap-bound and absent in virgin. |
| X7 touches | DROPPED | stats-era only. |
| X8 referee | DROPPED | coverage is zero in pre-stats seasons and the cards instrument itself fails. |
| X9 possession / big chance | DROPPED | stats-era only. |

Frozen constant: goals 1H share = 0.4482 from the DEV HT source. Count markets
have no halves constant and are FT-only.
