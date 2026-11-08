# Step 1 — Data Understanding: Italy Serie C (IT-SerieC)

Source: FotMob world warehouse, parent league_id **147**, index rows **6,184**.

## Inventory

| Season | Index / finished | Regular | Excluded other phase | Teams | Stats | Events | Referee |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2021/2022 | 1,154 / 1,154 | 1,102 | 52 | 59 | 0 | 1,050 | 0 |
| 2022/2023 | 1,190 / 1,190 | 1,140 | 50 | 60 | 0 | 1,089 | 0 |
| 2023/2024 | 1,190 / 1,190 | 1,140 | 50 | 60 | 0 | 1,087 | 0 |
| 2024/2025 | 1,118 / 1,118 | 1,066 | 52 | 58 | 0 | 1,022 | 0 |
| 2025/2026 | 1,146 / 1,146 | 1,102 | 44 | 59 | 0 | 1,060 | 0 |
| 2026/2027 | 386 / 386 | 386 | 0 | 60 | 386 | 350 | 223 |

The non-regular league names are `Serie C Super Cup`, `Serie C Promotion
Playoff`, and `Serie C Relegation Playoff`; their per-season counts are in
`inventory_summary.json`. Regular names are `Serie C Grp. A/B/C`.

## Coverage and format

- FT score is present in every finished payload (`header.status.scoreStr`).
- Stats are present **only in 2026/2027 (386/386)**; every earlier season is
  zero. Shotmap is zero everywhere. Period splits occur only in part of the
  in-progress 2026/2027 season. Thus SOT, corners, cards, and total shots have
  no target in a complete season and no development window.
- Referee text is empty in every complete season and present for only 223
  matches in 2026/2027. Events are present in the counts above, but event lists
  are not treated as a settlement-grade cards feed.
- Serie C has three regional groups of roughly 20 teams. The regular season is
  a within-group double round robin; inter-group promotion playoffs and
  relegation playouts follow. Groups do not meet in the regular season.
- The model uses **regular-phase matches only**: 5,936 of 6,184 finished
  matches. The 248 excluded matches are Super Cup/playoff/playout matches with
  knockout, inter-group, or different-incentive structure.

One pooled Dixon-Coles fit is appropriate for the regular phase as three
within-group rating systems sharing home advantage, mu, and rho. Team ratings
absorb group-level differences. `group` is an EDA dimension only, not a model
feature.
