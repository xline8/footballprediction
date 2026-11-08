# Step 5 — Features: IT-SerieC (X1–X9)

All features obey the causal contract: only matches strictly before the target
are available; absent fields are never fabricated.

| # | Feature | Verdict | Reason |
|---|---|---|---|
| X1 | Blend observation (goals + xG) | **ADOPTED, degraded** | xG is absent; the goals-only fallback applies to every match. |
| X2 | Mover tier offset (Serie B↔Serie C) | **DROPPED** | F4 offsets are small-sample and not stable enough to freeze. |
| X3 | Set-play xG decomposition | **DROPPED** | No xG. |
| X4 | xG-per-shot / ratio features | **DROPPED** | No shotmap or xG. |
| X5 | Finishing / form features | **DROPPED** | Forbidden program-wide and unsupported by available data. |
| X6 | xGOT era features | **DROPPED** | No shotmap/xGOT. |
| X7 | Box touches (corners) | **DROPPED** | Stats feed absent in complete seasons; corners not buildable. |
| X8 | Referee covariate (cards) | **DROPPED** | No complete-season referee coverage; cards not buildable. |
| X9 | Territorial / corners base pattern | **DROPPED** | No stats feed; corners not buildable. |
| SHRINK | Thin-data rating shrinkage | **ADOPTED as a pre-registered arm** | For teams with fewer than six prior in-league matches, scale ratings by n/6. |

## Halves constants

None. This is an FT-only product.
