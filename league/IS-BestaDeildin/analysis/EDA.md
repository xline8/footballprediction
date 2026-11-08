# EDA — IS-BestaDeildin

## F1 — Levels and home advantage

Per-match goals are 2.83, 3.52, 3.46, 3.56, 3.32 and 3.99 for 2021–2026.
Stats-era values for 2023–2025 are SOT 9.80/10.68/9.90, corners
11.34/12.05/11.72, shots 26.83/28.88/28.09, and stats yellows
4.17/4.97/4.78. Virgin 2026 is hot: SOT 11.41, corners 12.49, shots 32.65,
yellows 4.09. Home goals exceed away goals in every season. Dev over-rates at
the frozen primary lines are goals OU2.5 .6590, SOT 9.5 .5453, corners 11.5
.5103, cards 4.5 .4856 and shots 27.5 .5021.

## F2 — Reliability

The deterministic career-pooled split-half recomputation gives goals-for
r=.812, SOT-for .802, corners-for .790, shots-for .869, possession .930,
box-touches-for .848 and yellows-for .040. The coordinator’s seed-fixed
reference values are retained in the brief (SOT .92, corners .83, shots .87,
goals .89, possession .93, box .68, yellows .20). This is a convention/seed
difference, not a change to the frozen feature verdicts.

## F3 — Halves

Frozen constants are goals .4455, SOT .4644, corners .4707, shots .4623 and
yellows .3499. The split subset is 414 matches for SOT/corners/shots (407 for
yellows after missing values). Observed versus binomial variances are recorded
in `eda_summary.json`; halves are presentation-only league constants.

## F4 — Cards artefact

Stats yellows are frozen as target. Exact stats/event agreement is 86.4% in
2023, 76.5% in 2024, 70.4% in 2025 and 82.1% in 2026 in this recomputation;
the coordinator reports 86.4%, 76.5%, 82.1% for 2023/2024/2026 and identifies
2025 event data as defective (27 zero-event matches versus 2 stats). The
coherent decision is stats `yellow_cards`, with event values retained only for
the check.

## F5 — Box artefact and phase levels

2023 box touches average 10.4 versus 51.1 in 2024 and 52.3 in 2025, so X7 is
restricted to 2024+. Coordinator phase levels are regular 3.375,
championship 3.853 and relegation 4.013 goals per match; the rebuilt CSV’s
pooled values are in `eda_summary.json` and include 2026.

## F6 — Referees and coverage

Named referees are 81/162, 126/162, 130/162 and 65/162 in 2023–2026. The
builder finds 16 referee labels and deterministic split-half r=.394; the
coordinator’s seed-fixed value is r≈.71 over 16 referees and 337 dev matches.
X8 remains adopted for the preregistered cards gate, with virgin coverage a
risk note.
