# Verdict — G-J2 (J2 goals model)

Date: 2026-11-09. Branch `build/g-j2`. Pre-registration:
`league/J2/prereg/PREREG_G_J2.md` (commit `3da3e8d`, frozen before
any fitting). Engine: `league/J2/engine/goals/g_j2.py` (J2's own
engine, seeded from the production Dixon-Coles pattern in
`model_v2.py`). Implementation by Codex (gpt-5.6-luna) under
coordinator brief; verification independent (see §4).

## 1. Dev results (walk-forward, monthly, expanding; 2021–2024, n=1,764 scored, 2021-02 excluded)

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | 1.0879 | 0.2240 | 0.7456 |
| X2 (cross-tier priors) | 1.0883 | 0.2241 | 0.7455 |
| Climatology / base rate | 1.0927 | 0.2308 | 0.6904 |

Per season (1X2 LL / OU2.5 LL):

| Season | n | GZ LL | X2 LL | Clim. LL | GZ OU | X2 OU | Base OU |
|---|---|---|---|---|---|---|---|
| 2021 | 451 | 1.1621 | 1.1621 | 1.0996 | 0.8259 | 0.8259 | 0.6889 |
| 2022 | 465 | 1.0915 | 1.0911 | 1.0964 | 0.6940 | 0.6944 | 0.6868 |
| 2023 | 465 | 1.0725 | 1.0742 | 1.0922 | 0.7602 | 0.7595 | 0.6924 |
| 2024 | 383 | 1.0149 | 1.0150 | 1.0804 | 0.6959 | 0.6960 | 0.6942 |

Movers receiving an X2 prior: 2021: 0 (no 2020 data in corpus),
2022: 6, 2023: 4, 2024: 3.

## 2. Gate legs

Dev gate — pooled dev 1X2 LL and RPS beat climatology and OU2.5 LL
beats base rate, else arm dead:

- 1X2 LL leg: **PASS** both arms (1.0879 / 1.0883 < 1.0927).
- RPS leg: **PASS** both arms (0.2240 / 0.2241 < 0.2308).
- OU2.5 LL leg: **FAIL both arms** (0.7456 / 0.7455 vs base rate
  0.6904 — the model is far *worse* than the constant base rate).

**Both arms are dead at the dev gate.** Per the prereg and
MODEL_DESIGN §2 ("NOT built if the dev walk-forward gate fails"),
the virgin window was **not read**: season 2025 remains untouched
by this candidate, no virgin predictions were generated, and the
both-pass / virgin legs (i)–(ii) are moot. Leg (iii) for the record:
both arms beat climatology on dev 1X2 LL in 3 of 4 seasons (all but
the 2021 cold start), so both would have been both-pass-eligible
had they survived.

**Shipped arm: none. Verdict: FAIL.**

## 3. Why the OU leg fails (diagnosed, not assumed)

The failure is concentrated in season-opening months (worst OU LL:
2021-03 = 1.53, 2023-03 = 1.28, 2021-04 = 1.00; 9 of 42 months
above 0.75). Mechanism: the unmodified production fit, refit monthly
on an expanding window, assigns extreme ratings to teams with one
or two matches in the training set — exactly the movers and
early-season teams J2 has every year. Examples from March 2023
(Gate Zero): Shimizu S-Pulse (relegated from J1, two low-scoring
February matches in training) priced at λ = 0.02 / 0.01
(p_over ≈ 0.000) in matches that finished 1–3 and 2–2; Iwaki FC
(promoted from J3) priced at λ_home up to 3.08 in matches that
finished with one goal. Mean predicted total goals is well
calibrated (2.42 vs 2.47 actual pooled); the damage is per-match
extremes, which log-loss punishes without mercy. The X2 prior as
pre-registered (initialisation only) does not cure this: once a
mover has a February match or two in training, the sweeps wash the
prior out, and X2's pooled OU LL (0.7455) is indistinguishable from
Gate Zero's. X2 also does not beat Gate Zero on 1X2 LL pooled
(1.0883 vs 1.0879) — the cross-tier prior, in this form, buys
nothing measurable in J2.

## 4. Verification (independent of the implementer)

- The coordinator re-ran the dev harness using the **production
  `model_v2.DC` class itself** on the J2 data: it reproduces the
  engine's dev numbers essentially exactly (pooled LL 1.0879, OU
  0.7456, per-season identical; RPS 0.224), cold- and warm-started.
  The engine is a faithful copy of the reference pattern; the OU
  failure belongs to the pattern in this league, not to the copy.
- Two implementer bugs were caught in verification and fixed before
  this verdict: (1) an RPS cumulative-actual bug (home wins counted
  twice; reported RPS 0.527 → correct 0.224); (2) the virgin
  walk-forward's training set was restricted to the evaluated
  seasons (would have trained 2025 on 2025 only) — restructured to
  train on full history. Virgin mode was then deliberately **not
  run** (see §2).
- Spot-check of virgin predictions by hand: not applicable — no
  virgin predictions exist, by the gate decision above. Dev
  predictions were spot-checked instead (lambdas recomputed from
  the fit for March 2021/2023 samples; the extreme-λ cases in §3
  are quoted from that check).

## 5. What would have to change (for the record, not done)

Nothing here is a tuning suggestion to apply silently. The honest
reading: the production DC pattern, unmodified, is not safe in a
league with yearly movers and thin early-season data, because its
fit has no shrinkage floor for thin-data teams. Any revival of
G-J2 needs a new pre-registration (e.g. a rating-shrinkage /
prior-strength arm, or excluding season-opening months from the
OU gate with the exclusion named in advance) and a fresh virgin
window decision by the user — season 2025 is still virgin and
available for exactly one such future read.
