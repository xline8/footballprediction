# S-MX Verdict — Liga MX shots-on-target model

Date: 2026-11-09. Branch `build/mx-ligamx`. Prereg:
`league/MX-LigaMX/prereg/PREREG_S_MX.md` (commit 8512c8d, frozen
before any fitting). Engine: `league/MX-LigaMX/engine/sot/`.
Implementation by Codex (gpt-5.6-luna) under the two-agent flow;
the coordinator caught and had fixed an AR-port bug in the
baseline/virgin path before the virgin read, and independently
re-ran the dev harness (see Verification notes). Predictions-only
product: no Liga MX SOT odds source exists in-system — expected,
not a defect.

## Verdict: FAIL — both dev-passing arms fail virgin leg (i); nothing ships

GZ and RS pass the dev gate and are read on the virgin; X4 fails
the dev gate (pooled LL@8.5 loses to the naive trailing-10) and is
not read. On the virgin, both read arms are well calibrated
(−0.18pp / −0.19pp) but both lose the LL leg to the **naive
trailing-10 baseline** (0.6721), which had a strong virgin block.
Nothing ships. The Gate Zero virgin predictions file exists as the
prereg-pattern fallback, labelled as such here — it is **not** a
shipped product.

## Dev results (per-match walk-forward, scored blocks = tournaments 2–9, n = 1,224; LL@8.5)

Pooled:

| Arm | LL@8.5 | vs base 0.7133 | vs naive 0.6828 |
|---|---|---|---|
| GZ | **0.6816** | pass | pass (by 0.0012) |
| RS | **0.6814** | pass | pass (by 0.0014) |
| X4 | 0.6833 | pass | **FAIL** |
| League base rate | 0.7133 | — | — |
| Naive trailing-10 | 0.6828 | — | — |

Per-block LL@8.5:

| Block | GZ | RS | X4 | Base | Naive |
|---|---|---|---|---|---|
| 2021/2022 - Clausura | 0.6905 | 0.6904 | 0.6906 | 0.7832 | 0.6888 |
| 2022/2023 - Apertura | 0.6881 | 0.6866 | 0.6935 | 0.7224 | 0.6980 |
| 2022/2023 - Clausura | 0.6608 | 0.6607 | 0.6598 | 0.7243 | 0.6597 |
| 2023/2024 - Apertura | 0.6753 | 0.6733 | 0.6781 | 0.7051 | 0.6918 |
| 2023/2024 - Clausura | 0.6923 | 0.6908 | 0.7027 | 0.6933 | 0.6834 |
| 2024/2025 - Apertura | 0.6911 | 0.6919 | 0.6891 | 0.6924 | 0.6896 |
| 2024/2025 - Clausura | 0.6665 | 0.6687 | 0.6692 | 0.6932 | 0.6558 |
| 2025/2026 - Apertura | 0.6884 | 0.6885 | 0.6832 | 0.6922 | 0.6955 |

Sign check (variant dev LL ≤ GZ, of 8): RS 5/8 (passes leg iii),
X4 3/8 (would also have failed leg iii).

## Virgin results (2025/2026 - Clausura, n = 153, read once)

| Arm | LL@8.5 | Calibration diff | SE |
|---|---|---|---|
| GZ | 0.6780 | −0.18pp | 3.99pp |
| RS | 0.6776 | −0.19pp | 3.99pp |
| League base rate | 0.6908 | −4.36pp | — |
| Naive trailing-10 | **0.6721** | +1.05pp | — |

## Gate arithmetic

- Dev gate (pooled LL@8.5 must beat BOTH baselines): GZ **pass**,
  RS **pass**, X4 **FAIL** (0.6833 > naive 0.6828).
- Virgin leg (i) (LL ≤ Gate Zero's AND ≤ best baseline's): GZ —
  ≤ itself, but 0.6780 > 0.6721 (naive) → **FAIL**. RS — ≤ GZ
  (0.6776 < 0.6780), but 0.6776 > 0.6721 → **FAIL**.
- Virgin leg (ii) (calibration): both arms pass clean
  (|diff| ≤ 1.0pp).
- Virgin leg (iii): RS 5/8 passes; moot given leg (i).
- No arm passes all legs → **S-MX is FAIL; nothing ships.** The
  virgin block's SOT ran at the dev level (9.13 vs 8.92 mean) but
  the naive trailing-10 — a component of the model itself, used
  here as the standalone baseline — tracked it better than the
  full v5 ensemble did. Recorded plainly: on this window the
  ratings machinery subtracted value against its own naive term.

## Verification notes (coordinator, independent of Codex)

- **Port bug caught before the virgin read**: the AR/NL-derived
  harness computed the league base rate at line 7.5 (AR's primary)
  and carried AR season labels, AR halves constants (0.459/0.541)
  and an X6 judging branch in its virgin path. All were fixed to
  the MX prereg (per-line base rate; MX labels; 0.455/0.545; X6
  removed; xGOT loading disabled — no MX arm may read xGOT) and
  dev was re-run: arm pooled LLs were **unchanged** by the fix;
  only the baseline moved (ll_8.5 0.7033 → 0.7133, the correct
  at-line prior-rate baseline), and the dev gate outcome was
  unchanged.
- Coordinator re-run of the fixed dev harness reproduces every
  pooled and per-block number (float agreement to ~1e-13).
- Virgin read arms were exactly the dev-passing arms (GZ, RS);
  X4 was not read. Fallback predictions are Gate Zero's, in
  `predictions/s_mx_virgin_predictions.csv` (153 rows), with
  fitted params in `engine/sot/fitted_params_virgin.json` —
  retained as the prereg-pattern record of the read, not a ship.
