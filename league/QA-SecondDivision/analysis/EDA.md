# Step 3 — EDA: QA-SecondDivision

All numbers from `analysis/eda.py` (`eda_summary.json`). Fitting-relevant
numbers use DEV-ERA data only: G dev = 2024/2025; S/C/T/K dev = 2025/2026.
The 2025/2026 goals levels and the 2026/2027 levels appear in the inventory
table only (descriptive, QA-QatarStars convention) and are never used to
choose G lines, arms, or windows.

## F1 — Levels (per match, H+A totals unless noted)

| Season | Goals | Home–Away | SOT | Corners | Shots | Yellows (events) | Yellows (stats) |
|---|---|---|---|---|---|---|---|
| 2024/2025 (n=56; stats n=38) | 2.61 | 1.45–1.16 | 7.89 | 8.92 | 23.26 | 5.25 | 5.05 |
| 2025/2026 (n=56) | 3.02 | 1.43–1.59 | 8.64 | 9.73 | 23.12 | 5.21 | 4.70 |
| 2026/2027 (n=29, in progress) | 2.76 | 1.31–1.45 | 9.00 | 8.21 | 26.41 | 4.17 | 3.76 |

- Goals/match 2.61 in the G dev season (OU2.5 over-rate 44.6%); the parent
  Stars League sits higher (3.05–3.65). Home advantage is near-absent and
  flips sign across seasons (see DATA_UNDERSTANDING) — the DC fit's single
  home intercept is a known risk here, exactly as in QA-QatarStars (where
  it contributed to the G FAIL).
- SOT/corners/shots levels are close to the J1 reference points (J1 SOT
  ~9, corners ~10, shots ~24); the league is not an outlier in volume.
  Yellows run high (5.2 events/match in both complete seasons vs ~4.5 in
  the Stars League stats era) and fall to 4.17 in the partial 2026/2027
  (n=29 — do not over-read a partial season).
- The G dev scored block (2024/2025 rounds 8–14) averages 2.43 goals/match
  vs 2.79 in the warm-up rounds 1–7 — the scored block is the lower-scoring
  half of the season; the dev gate is read on that block as frozen.

## F2 — Team traits: NOT demonstrably reliable (the honest finding)

Split-half r (odd/even chronological team matches; programme method), with
a chronological first-half/second-half sensitivity check. Pools: G dev =
2024/2025 (8 teams); stats pool = pre-scored-window stats matches
(2024/2025 stats era + 2025/2026 rounds 1–7; 9 teams — Al-Sailiya and
Al-Khor each contribute one season). With 8–9 teams the SE of r is ~0.35,
and the two split methods disagree on the same pool:

| Trait | Odd/even r (n) | Chrono r (n) | Per-season recheck |
|---|---|---|---|
| goals-for, G dev | −0.73 (8) | −0.74 (8) | — |
| goals-for, stats pool | −0.15 (9) | −0.19 (9) | — |
| SOT-for, stats pool | +0.55 (9) | +0.67 (9) | 24/25 +0.61, 25/26 +0.36 |
| shots-for, stats pool | +0.78 (9) | +0.74 (9) | — |
| corners-for, stats pool | −0.40 (9) | −0.60 (9) | 24/25 −0.33, 25/26 +0.38 (sign flip) |
| yellows-for, stats pool | −0.01 (9) | −0.28 (9) | — |
| possession, stats pool | +0.24 (9) | — | — |

Reading: **no trait clears a reliability bar in this league.** SOT-for and
shots-for are positive under both split methods with consistent per-season
signs for SOT, but n=9 puts the 95% CI roughly at [0.1, 0.9] — weak-positive
evidence, not a proven trait. Corners, goals, and yellows are zero or
negative with a sign flip across seasons (corners). The negative
goals-for r (−0.73, n=8) is within small-sample noise across the many
(trait × method × season) comparisons run here — it is reported, not
patched, and the dev gate arbitrates. Consequence: X5 trailing means enter
only as the reference architectures' own naive component (their justification
is the architectures' validation history, not a measured trait in this
league); no feature is adopted on the strength of these r's.

## F3 — Half shares: frozen constants justified (true variance ≈ 0)

Pooled 1H share, per candidate dev era (J1-style variance decomposition:
observed var of per-match shares minus mean binomial sampling var):

| Market | Dev era | Pooled 1H share | n total | True SD |
|---|---|---|---|---|
| goals (event times) | 2024/2025 | **0.4589** | 146 goals | 0.0 |
| SOT (splits) | 2025/2026 | **0.4194** | 484 | 0.0 |
| corners (splits) | 2025/2026 | **0.4495** | 545 | 0.010 |
| total shots (splits) | 2025/2026 | **0.4456** | 1295 | 0.0 |
| yellows (event times) | 2025/2026 | **0.3151** | 292 | 0.089 |
| yellows (stats splits, reference) | 2025/2026 | 0.3346 | 263 | 0.022 |

The per-match 1H share variance is ≈ binomial noise for goals, SOT, and
shots (true SD 0.0) — the frozen-constant presentation rule stands, and no
per-team/per-match 1H modelling is attempted (R1). Corners (0.010) and
stats-yellows (0.022) are negligible. Event-yellows show true SD 0.089 —
the largest in the table, driven by the small per-match counts (mean 5.21)
and the event feed's lumpiness; the constant is still frozen (a per-match
1H yellows model would be fitting noise at n=56), and the verdict records
the 0.089 as the known imperfection of the K 1H presentation.

## F4 — Movers / entrants (X2)

No within-league mover history exists before the G virgin: 2024/2025 is the
first warehouse season, so no team has a previous-season tier transition to
learn from. The ENTRANT arm therefore rests entirely on the QA-QatarStars
warehouse priors (see FEATURES.md / MODEL_DESIGN.md). The single entrant
into the G virgin season (Al-Khor, relegated from the Stars League) is a
virgin-season fact for G; its 2025/2026 performance plays no role in G's
design and is not reported here. For the stats markets, Al-Khor's entry is
pre-virgin and descriptive only (X2 is a goals feature; the S/C/T/K
engines meet a new team through league-mean fallbacks in their trailing
windows, documented in MODEL_DESIGN.md).

## F5 — Lines (dev-season over-rates, closest to 0.5 — mechanical)

| Candidate | Dev season (n=56) | Ladder over-rates | Primary |
|---|---|---|---|
| G (OU goals) | 2024/2025 | 1.5: 0.732, 2.5: 0.446, 3.5: 0.268 | **2.5** |
| S (SOT) | 2025/2026 | 7.5: 0.554, 8.5: 0.482, 9.5: 0.339 | **8.5** |
| C (corners) | 2025/2026 | 8.5: 0.661, 9.5: 0.464, 10.5: 0.339 | **9.5** |
| T (shots) | 2025/2026 | 22.5: 0.571, 23.5: 0.446, 24.5: 0.393 | **23.5** |
| K (yellows, events) | 2025/2026 | 3.5: 0.750, 4.5: 0.589, 5.5: 0.500 | **5.5** |

K note: the event-unified line is 5.5 (exactly 0.500), not the production
cards model's customary 4.5 — the programme's closest-to-0.5 rule is
mechanical, and 4.5 sits at 0.589. (For reference, stats yellows would give
4.5 at 0.536 — but the target is events, so the events ladder governs.)

## F6 — Referee (X8): absent

0 named referees in both dev seasons (2024/2025, 2025/2026); 1 in 2026/2027.
No referee rate is measurable on dev. X8 dropped.

## F7 — Thin-corpus caveat (read before the gates)

- G dev scored n=28; S/C/T/K dev scored n=28; G virgin n=56; S/C/T/K
  virgin n=29 (partial). At n=29 the calibration SE is ≈9pp, so the ≤1 SE
  provisional band is wide; the gate is applied mechanically regardless,
  and the verdicts record the virgin as TRANSITIONAL with a confirmatory
  read at season end.
- Dev LL comparisons at n=28 are noisy: a dev-gate pass/fail on 28 matches
  is a weak discriminator, and the verdicts must say so plainly either way.
