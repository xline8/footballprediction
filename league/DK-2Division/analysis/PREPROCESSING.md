# Preprocessing — DK-2Division

Retain played, non-cancelled matches with complete FT scores. All 1,050 rows are included. Season labels are the warehouse labels.

Derive `phase=regular` for rounds 1–22 and `phase=split` for rounds 23–32. Rows remain ordinary observations; the fixture graph, not feed group labels, verifies the format.

Use HT scores only where exactly one Half event carries both scores. Missing HT scores remain empty; they are never fabricated from events or full-time scores. Reds and events are audit fields only. No stats, shotmap, xG, player, or referee values are imputed.
