# France Ligue 2 — feature decisions (X1–X9)

All values below are from `analysis/eda_numbers.json`; features are trailing/expanding and strictly pre-match.

| Feature | Decision | In-league evidence |
|---|---|---|
| X1 xG blend | DROPPED | Expected-goals coverage is 0.3%, 0.8%, 0%, 1.6% in development; 100% in 2025/2026. |
| X2 mover offset | ADOPTED candidate | Ligue 1 entrants: GF delta +0.227 and GA delta −0.151; Ligue 3 entrants: GF −0.177 and GA +0.161 per team-match. |
| X3 set-play xG | DROPPED | Set-play xG is unavailable for a usable development window. |
| X4 xG/shot SOT quality | DROPPED | Shotmap coverage is 0.3%, 0.8%, 0%, 1.6% in development and 100% in the virgin. |
| X5 SOT base | ADOPTED | SOT split-half reliability is 0.639; total-shots reliability is 0.715. |
| X6 xGOT | DROPPED | xGOT is confined to the virgin-era shot data. |
| X7 box-touch corners | ADOPTED candidate | Box-touch reliability is 0.771 for and 0.732 against. |
| X8 referee cards | DROPPED | Referee coverage is 50.0% in the seed and 82.7% in the virgin; reliability is in the EDA JSON. |
| X9 corners covariates | ADOPTED candidate | Corners reliability is 0.606; big-chance reliability is 0.713. |

## Frozen halves constants

Complete-splits era (2023/2024–2025/2026): goals 0.4457, SOT 0.4738, corners 0.4803, total shots 0.4702, event yellows 0.3736. The EDA JSON records observed variance versus sampling noise.
