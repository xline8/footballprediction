# Step 5 — Features: CO-PrimeraA (J1 X1–X9 template applied)

Global causality contract as in `league/J1/analysis/FEATURES.md`
(features use only matches strictly before kickoff; ratio features
are ratios of sums; a window that cannot be filled makes the arm
inactive for that match, never filled from the future). Era facts
that govern this league: count stats exist from 2021; card EVENTS
from 2023 - Apertura; period splits from 2023 - Clausura; stats xG
and shotmap only from 2025 - Clausura (the virgin boundary).

| # | J1 feature | CO-A verdict | Reason (with number) |
|---|---|---|---|
| X1 | Blend observation (goals + xG) | **ADOPTED, reduced** | Goals present 2,582/2,582. Stats-feed xG present in ≤4.4% of every dev tournament except the last (2025-Cl) — a blend arm would be active in 1 of 9 dev blocks and is not dev-gatable. The reference blend's documented goals-only fallback applies. |
| X2 | Mover cross-tier prior | **ADOPTED as arm X2 (goals)** | Primera B (id 9125) IS in the warehouse; exactly 2 promotions/year, every absent club is a B promotion. Dev-era promoted arrivals (2022–2025, 8 club-years): ΔGF −0.217/m (8/8 negative), ΔGA +0.200/m (6/8 positive) vs the per-team base 1.1235 (EDA F4). Frozen form: for a club flagged `mover_up` for calendar year Y (absent from A in Y−1, present in B in Y−1), its fitted ratings are replaced at prediction time by a = ln(0.81), d = ln(1.18) for that year's predictions. Offsets from dev-era arrivals ONLY. |
| X3 | Set-play xG decomposition | **DROPPED** | `expected_goals_set_play` exists only from 2025 - Clausura (1 of 9 dev blocks). An era starting at the virgin boundary cannot be fitted or gated (ES-LaLiga2 lesson). |
| X4 | xG per shot (shotmap) | **DROPPED** | Shotmap empty until 2025 - Clausura (0–4.4% in every earlier dev tournament). Same era verdict as X3. |
| X5 | Trailing target-rate means (naive / ensemble components) | **ADOPTED** | Target traits are reliable here (EDA F2: SOT-for 0.828, corners-for 0.452, shots-for 0.684, ev-yellows-for 0.585 era-restricted). Consumed by the count engines' naive/ensemble components and the harness baselines, era-restricted for cards (2023+). |
| X6 | Attacking xGOT per shot | **DROPPED** | xGOT exists only inside the shotmap era (2025-Cl onward). Same era verdict as X3/X4. |
| X7 | Opp-box touches for/against (corners multiplier) | **ADOPTED as arm X7 (corners)** | Trait for 0.451 / against 0.640; per-match corr with corners-for 0.503 — above J1's 0.471 where the arm is proven. Coverage quirk honoured by the min-8 rule: touches present in only ~0.48–0.55 of 2021–2023 Clausura matches (1.000 from 2024), so the arm is inactive where its window cannot be filled. |
| X8 | Referee yellow rate (trailing) | **ADOPTED as arm X8 (cards)** | Cards-era coverage 0.94 (2023-Cl…2025-Cl; PY dropped at 0.111 — not comparable); strictness split-half r = 0.487 on 36 referees with ≥8 era matches (EDA F5). Trailing mean of event-unified yellows within this league, shrunk toward the league mean; referees with <8 prior era matches take the shrunk league mean. Leakage guard: only the referee's matches strictly before kickoff count; the appointment itself is a fixture fact. |
| X9 | Production corners covariates (possession, big chances) | **ADOPTED** | Both keys present in ~100% of matches from 2021; traits: possession 0.837, big-chances-for 0.744; corr(possession, corners-for) 0.406. Carried unchanged inside corners Gate Zero, as in production. |
| ALT | Altitude (venue elevation) | **DROPPED** | The payload carries stadium name/city/coords but NO elevation field; no in-corpus altitude measure exists. (MX-LigaMX measured altitude from an external table and did NOT adopt it — collinear with team identity. Here it is not even measurable from the corpus, so it is dropped at the data test, not the reliability test.) Bogotá/Tunja/Pasto venues are noted in EDA context only. |
| SHRINK | New-team rating shrinkage (goals variant) | **NOT REGISTERED (degenerate)** | At every dev tournament start the only <6-prior clubs are the two promoted clubs at exactly 0 priors, for whom shrinkage ≡ Gate Zero's unseen=mean rule (EDA F4). The arm would be bit-identical to Gate Zero on every dev/virgin prediction (GE/BG2 precedent). The promoted-club failure mode is carried by X2, which has real evidence here. |

Rejected outright (J1 §3 analogues): per-team/per-match half shares
(R1 — EDA F3 true variance ≈ 0 for all five markets), finishing /
conversion covariates (R2/R3 — no dev-era xG to define them),
standalone trailing on-target rate as a covariate (R4 — the trait is
real here, r = 0.774, but it is exactly v5's internal Beta-Binomial
ratio component; the standalone covariate is the rejected object, as
in J1), lineup/absence (R6, closed programme-wide), standings/h2h
snapshots (R9, post-match leakage), attendance (R10, not pre-match),
reds as target (R12).

## Adopted variant mechanisms (pre-registered in the preregs)

- **X2** (goals) — cross-tier mover prior as above.
- **RS** (SOT) — the v5 pattern's harder on-target-ratio shrinkage
  (prior 200 → 20,000), the AU/SA/PY-winning configuration, registered
  as S-COA's single variant arm.
- **X7** (corners) — opp-box-touches territorial multiplier as above.
- **X8** (cards) — referee multiplier as above.
- **Total shots** — the shots family's three standard arms A (v1
  pattern), B (v2 level layer), C (E9 trailing-r); no league-specific
  feature is consumed.

## Halves constants (frozen, presentation only — EDA F3)

goals **0.4706** · SOT **0.4862** · corners **0.4956** · total shots
**0.4850** · cards **0.3543**. FT + 1H/2H splits on PASS only; halves
never enter any gate.
