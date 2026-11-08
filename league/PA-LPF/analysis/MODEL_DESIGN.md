# PA-LPF model design

Only **G-PA-LPF** is buildable: production Dixon–Coles goals-only reference,
`hl=270`, rho grid (0.0, −0.05, −0.10, −0.15) chosen by weighted LL,
`MAXG=10`, and tau low-score correction. S/C/K/T are NOT BUILDABLE; their
not-buildable prereg is Phase B. Arms are Gate Zero and SHRINK, exactly the
G-J2 lesson: for fewer than six prior matches use factor `n/6`. EDA F4:
the only sub-6-prior teams are n = 0 newcomers (Veraguas United 2024,
SD Atletico Nacional 2025, Union Cocle 2026), so SHRINK is expected
DEGENERATE (≡ Gate Zero) under this season-blocked walk-forward — a
design note to verify from dev output, as in AM.

Seed 2023 is partial; scored folds are 2024+2025, pooled awarded-excluded
regular n=382. Virgin 2026 is transitional and incomplete (Clausura complete,
Apertura rounds 1–15), n=186, read once only for dev-passing arms; confirmatory
season-end reread is reserved. Primary line is OU 2.5 from development.
Climatology uses prior seasons only; trailing-10 GF/GA is reported, not gated.
Halves are presentation only using frozen 0.449173 for FT/1H/2H.

Dev gate: pooled 1X2 LL + RPS beat climatology AND OU2.5 LL beat the base-rate
baseline. Virgin legs: (i) LL ≤ Gate Zero and ≤ climatology, (ii) pooled
home-win and OU2.5 calibration absolute error ≤1.0pp, and (iii) per-season
sign check. A breach within 1 SE is PROVISIONAL PASS; both-pass ships the
lower pooled virgin 1X2 LL. Gate Zero dev failure makes variants moot and the
virgin unread. No fitting, predictions, walk-forward, or harness runs occur
in Phase A. Thin window: four seasons, seed 120, dev 382, virgin 186.
