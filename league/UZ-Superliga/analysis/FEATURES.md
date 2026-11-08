# Phase 3.5 — Features: Uzbekistan Superliga (J1 X1–X9 template)

A feature is adopted only if the data exists AND its reliability check
passes in THIS league. Every J1 template feature is DROPPED here — the
data is absent in 215/215 payloads (scores-only league), and no
reliability check can be run on data that does not exist.

| Feature | Verdict | Reason (reliability number where applicable) |
|---|---|---|
| X1 — Blend observation pair (goals-model training input) | DROPPED | No xG in any payload (`content.stats` null 215/215); there is no second observation to blend with goals. No model built. |
| X2 — Mover tier offset (prior for promoted/relegated clubs) | DROPPED | No Uzbek sibling league exists in the warehouse (540 is the only Uzbekistan id); no promotion/relegation history (single season 2026). No mover prior exists. |
| X3 — Set-play xG share and rate (trailing) | DROPPED | No shotmap/xG in any payload (`shotmap.shots` empty 215/215). |
| X4 — xG per shot (trailing) | DROPPED | No shotmap/xG in any payload. |
| X5 — Trailing target-rate means (naive / ensemble components) | DROPPED | Trailing means are computable descriptively from scores, but there is no dev window to validate them against and no virgin to test them on; adopting them would be fitting without a gate. |
| X6 — Attacking xGOT per shot (trailing, era-guarded) | DROPPED | No shotmap/xG in any payload. |
| X7 — Opp-box touches for / against (trailing) | DROPPED | No stats block in any payload. |
| X8 — Referee yellow rate (trailing) | DROPPED | Referee blank 215/215; Card events sparse (29 in 99 matches with an event feed). No referee signal exists. |
| X9 — Reference territorial covariates (corners Gate Zero arm) | DROPPED | No corners in any payload. |

## Halves constants

None frozen. HT scores exist for 99/215 matches with a measured HT
share of goals of 0.4588, but coverage is late-season only (rounds 10,
14–27) and no halves presentation ships — freezing a constant from a
biased 99-match subset would be fabrication-adjacent. The FT-only
presentation is the only honest one, and nothing ships under this
verdict anyway.

## Consumption map

No design consumes any feature: no candidate reaches design
(see `MODEL_DESIGN.md`). The one measured trait with a real signal —
team attack rate, split-half r = 0.696 within 2026 — is recorded in
`EDA.md` as description, not adopted as a feature, because there is no
gateable window to validate it in.
