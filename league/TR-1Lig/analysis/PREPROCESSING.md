# TR-1Lig preprocessing and frozen windows

For every fit or score, include only finished regular-season rows with
`awarded=0`. Play-offs are excluded from all fits and scores by the frozen
`phase` rule. Awarded rows are excluded by the flag everywhere, regardless of
the displayed 3–0 score. Team identity is the FotMob team ID, never the text
name.

Development is season-blocked: seed 2021/22, scored seasons 2022/23–2024/25.
The 2025/26 complete regular season is virgin and is read once only after a
passing dev arm; 2026/27 is reserved and not read for fitting or gates. Phase A
itself performs no fitting and no virgin read. Count markets are FT-only because
their splits are fragment/virgin-only. Goals may use the event HT source for a
presentation constant only.
