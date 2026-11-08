# Step 6 — Model design: Indonesia Super League

## Feasibility matrix

| candidate | target in data? | virgin (2025/2026) contains target? | verdict at design |
|---|---|---|---|
| G-ID goals | yes (scores, all seasons) | yes (306) | BUILD |
| K-ID cards | yes (event yellows, complete-feed rows) | yes (306/306 complete) | BUILD |
| S-ID SOT | stats era only, ends Oct 2023 (+8 in 2024/2025) | **no (0 rows)** | NOT BUILDABLE |
| C-ID corners | stats era only, ends Oct 2023 (+8 in 2024/2025) | **no (0 rows)** | NOT BUILDABLE |
| T-ID total shots | stats era only; 2023/2024 values corrupt (SOT copies) | **no (0 rows)** | NOT BUILDABLE |

S/C/T get verdict documents recording NOT BUILDABLE with the era
evidence; no prereg is written and nothing is fitted for them
(TH-ThaiLeague2 precedent).

## G-ID — goals

- Reference: production Dixon–Coles pattern (the programme's shared
  `dc.py`), goals-only (X1 dropped), half-life 270 days, rho grid
  (0, −0.05, −0.10, −0.15), fit on all regular matches strictly before
  each scored season (season-blocked walk-forward).
- Arms (frozen in PREREG_G_ID): `gate_zero`; `shrink` — ratings of
  teams with fewer than 6 prior in-league matches are scaled toward
  the league mean by n/6 (the template-sanctioned answer to the
  new/promoted-team opener problem; with 3 promoted teams per season
  and no tier-2 data, this is the only mover treatment available).
- Windows: seed 2021/2022; dev scored 2022/2023–2024/2025; virgin
  2025/2026 read once, only if an arm passes dev. 2026/2027 unread.
- Primary line OU 2.5 (dev over-rate 0.508). Gate legs as frozen in
  the prereg (1X2 LL + RPS vs climatology on dev; virgin LL ≤ Gate
  Zero and ≤ climatology; calibration on home-win and OU2.5 rates,
  |breach| ≤1pp clean, ≤1 SE provisional; per-season sign check;
  both-pass → lower virgin 1X2 LL ships, tie → simpler arm).
- Halves: frozen goals_1h_share 0.434, presentation only.

## K-ID — cards

- Target (frozen, with reason): **event-unified yellows** =
  direct Yellow + YellowRed events, home + away, scored only on
  events_complete matches. Reason: the stats feed has no cards key at
  all in this league, so events are the target by construction
  (RU-1Division precedent, same target definition). The artefact
  check the programme requires (stats-vs-events) cannot be run —
  there is no stats source to disagree with — and the substitute
  check is feed completeness, handled by the events_complete rule:
  a truncated feed is missing-data, never a zero.
- Reference: production cards pattern (decayed venue-split ratings,
  prior shrinkage K=8, half-life 270d, NB over-probability at the
  primary line; fallbacks = dev-era measured per-team means
  home 2.13 / away 2.33 yellows).
- Arms (frozen in PREREG_K_ID): `gate_zero`; `x5` — mu = 0.5·model +
  0.5·naive trailing-10 (X5 adopted; reliability 0.402/0.338). No
  referee arm (X8 dropped: no identity exists).
- Windows: seed 2021/2022 (267 scored rows); dev scored 2022/2023–
  2024/2025 (only events_complete rows enter state updates and
  scoring: 306 + 144 + 281 = 731 matches); virgin 2025/2026
  (306 complete rows) read once, only if Gate Zero passes dev.
  Truncated-feed matches are skipped entirely by the online state —
  they neither score nor update (their true yellow counts are
  unknown; using their partial counts would poison the ratings).
- Primary line 4.5 (dev mean 4.455, over-rate 0.452). Gate legs as
  frozen in the prereg (pooled dev LL < base-rate and < naive;
  virgin LL ≤ Gate Zero and ≤ climatology; calibration |breach|
  ≤1pp clean, ≤1 SE provisional; sign check; both-pass → lower
  virgin LL ships).
- Halves: frozen yellow_cards_1h_share 0.385, presentation only.

## What ships on PASS

Winning arm's per-match virgin predictions under `predictions/`
(force-added), fitted params JSON in the engine dir, verdict doc in
`reports/`. On FAIL: verdict doc only, nothing ships, virgin unread
if the failure was at dev.
