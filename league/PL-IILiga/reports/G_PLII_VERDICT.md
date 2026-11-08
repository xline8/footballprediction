# G-PL-II verdict

Preregistration: `prereg/PREREG_G_PLII.md`; calibration is
actual − predicted. **Virgin NOT read** (dev gate failed — see below).
No virgin file, fitted-params file, or predictions CSV exists for
this candidate.

## Dev (scored 2022/2023–2024/2025, n=927)

| arm / baseline | LL 1X2 | RPS | OU2.5 LL |
|---|---:|---:|---:|
| Gate Zero pooled | 1.085122 | 0.233701 | 0.711110 |
| SHRINK pooled | 1.085122 | 0.233701 | 0.711110 |
| climatology pooled | 1.073300 | 0.229922 | 0.692977 |

Per-season Gate Zero model vs climatology:

| season | LL 1X2 model / clim | RPS model / clim | OU2.5 LL model / clim |
|---|---|---|---|
| 2022/2023 | 1.083307 / 1.079678 | 0.231836 / 0.229522 | 0.690650 / 0.691783 |
| 2023/2024 | 1.107842 / 1.079064 | 0.234985 / 0.224833 | 0.717835 / 0.692898 |
| 2024/2025 | 1.064218 / 1.061160 | 0.234283 / 0.235412 | 0.724845 / 0.694251 |

The model is worse than climatology on 1X2 LL in **every** dev
season, on OU2.5 LL in **every** dev season, and on RPS in two of
three (2024/2025 is the single exception, by 0.0011). This is a
stronger failure than the parent tier (G-PL passed dev and failed
only the virgin LL leg) and the sibling tier (G-GR2 passed 1X2/RPS
and failed only OU2.5 LL).

## Gate arithmetic

- Dev leg 1X2 LL: **FAIL** — 1.085122 is not < 1.073300 (+0.0118).
- Dev leg RPS: **FAIL** — 0.233701 is not < 0.229922 (+0.0038).
- Dev leg OU2.5 LL: **FAIL** — 0.711110 is not < 0.692977 (+0.0181).
- Gate Zero is dead; SHRINK is moot (and identical: SHRINK ≡ Gate
  Zero in every row — the 1–5 prior-match band never occurs under
  season-blocked fitting; 0-prior teams are 7/6/6 per target season,
  and the two returning teams with priors, Chojniczanka 2023/2024
  and Pogoń Grodzisk Mazowiecki 2024/2025, each carry a full 34
  prior matches, so the shrinkage never bites).

G-PL-II verdict: **FAIL; nothing ships. Virgin deliberately NOT
read.** Prediction CSV: none. Fitted virgin params: none.

## Why it fails (diagnosis, not a rescue)

The failure is a level failure, not only a shape failure. Pooled
over dev, the model predicts mean home-win 0.4258 against an actual
0.4423 and mean P(over 2.5) 0.4497 against an actual over-rate of
0.5200 — a +7.0pp totals gap. Mean predicted total goals are
2.48–2.49 in every dev season against actual 2.63–2.81. The
mechanism is the churn: 7 of 18 teams (39%) are new every season,
and 33–39% of target-season team-appearances are 0-prior teams
sitting on the DC's a = d = 0 anchor, which implies λ_H ≈ 1.23–1.26
and λ_A = 1.00 — well below the league's actual 1.52/1.25. The
fitted home advantage (h ≈ 0.21–0.23, rho −0.05/0.0/−0.05) cannot
absorb that: the anchor is a property of the reference architecture
meeting a league where two in five teams are strangers every year.
No post-hoc arm is attempted; the prereg forbids one, and the
diagnosis points at the anchor/churn interaction rather than at a
tunable parameter.

## Verification (independent of the Codex-built harness)

- `dc.py` and `arms.py` are byte-identical to the GR-SuperLeague2
  engine except module docstrings; the production `model_v2.py`
  `DC` class was read line by line and the port matches it (14
  sweeps, damping 0.7, +0.25 smoothing, fitted home advantage,
  rho grid on goals only, no `mu` factor in either — `mu` is
  computed but unused in the port, as production has no `mu` at
  all; `MAX_TRAIN` 4000 exceeds the 1,236 dev rows, so no slicing
  difference).
- The coordinator recomputed every per-season model and
  climatology figure with an independent driver (production
  `model_v2.DC` directly, own train/target splits, own climatology
  and scoring) from `plii_matches.csv`: all 12 model/climatology
  cells match the harness to <1.2e-14, and the pooled rows recompute
  exactly. The dev path loads 1,236 rows (2021/2022–2024/2025)
  only; the harness asserts the forbidden seasons and no
  2025/2026 or 2026/2027 row is read anywhere in the dev path.
- The SHRINK-band counts were recomputed independently: 0 teams
  with 1–5 priors in every target season.

## Non-buildable candidates (payload-level evidence)

- S-PL-II (SOT), C-PL-II (corners), K-PL-II (cards), T-PL-II (total
  shots): **not buildable** — `content.stats` is null and the
  shotmap is empty in all 1,679 payloads (builder-asserted); no
  referee is named in any payload; no period splits exist. The
  event feed carries goals plus dismissal-only Card events (173 Red
  + 192 YellowRed, zero plain-Yellow in 1,679 matches), so there is
  not even a yellow-card target to unify against. No dev or virgin
  evaluation was run for any of them, and none was preregistered.
