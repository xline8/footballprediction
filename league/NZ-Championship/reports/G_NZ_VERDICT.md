# G-NZ verdict — FAIL — virgin not read

Prereg: `prereg/PREREG_G_NZ.md`. Dev pooled n=92 (seasons 2023–2024).
Virgin 2025 (n=56, complete) was **NOT read** because Gate Zero failed
the dev gate; per the frozen rule the variants are moot and no arm ships.

## Dev pooled metrics

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---:|---:|---:|
| Gate Zero | 1.127229 | 0.263013 | 0.598031 |
| SHRINK | 1.127229 | 0.263013 | 0.598031 |
| Climatology | 1.057336 | 0.250859 | 0.568388 |
| OU2.5 base rate (0.75) | — | — | 0.562335 |

## Dev per season (1X2 LL / RPS / OU2.5 LL)

| Season | Gate Zero | SHRINK | Climatology 1X2 LL / RPS / OU LL |
|---|---|---|---|
| 2023 | 0.969155 / 0.218764 / 0.529737 | identical | 1.054884 / 0.258958 / 0.581191 |
| 2024 | 1.285303 / 0.307262 / 0.666326 | identical | 1.059789 / 0.242760 / 0.555585 |

## Gate arithmetic

Dev gate (prereg): pooled dev 1X2 LL and RPS must beat climatology,
and OU2.5 LL must beat the base-rate baseline. Gate Zero fails all
three legs: 1X2 LL 1.127229 > 1.057336 (+0.0699), RPS 0.263013 >
0.250859 (+0.0122), OU2.5 LL 0.598031 > 0.562335 (+0.0357). The failure
is decisive, not marginal — the fitted model is worse than predicting
the pooled prior-season outcome rates on every leg. SHRINK is
bit-identical to Gate Zero (0 lambda differences in either dev season:
with season-blocked fits, the only team with a training-window count
below 6 is Miramar Rangers with 5 matches in 2022, and Miramar plays
no match in either dev season, so the min(1, count/6) factor changes
nothing). Its sign check passes 2/2 on ties, which is moot once Gate
Zero fails dev.

## Diagnosis (descriptive, not a rescue)

- The dev outcome is a tale of two seasons. 2023 passes all three
  legs; 2024 fails all three badly (1X2 LL 1.285303 vs climatology
  1.059789). The pooled gate is sunk by 2024 alone.
- In both dev seasons the model is systematically home-tilted and
  goal-shy against what happened: 2023 predicted mean H/D/A
  0.473/0.230/0.297 against actual 0.391/0.152/0.457, and predicted
  mean OU2.5 over-rate 0.634 against actual 0.739; 2024 predicted
  0.411/0.206/0.383 against actual 0.370/0.196/0.435, and 0.647
  against actual 0.761. Away wins outnumbered home wins in both
  seasons, and the league scored 4.13 and 3.80 goals/match — the
  ratings fitted on 38–84 prior matches did not carry across the
  season boundary.
- This is the F2 warning made concrete: team traits replicate weakly
  here (split-half GF r=0.2293, GA r=0.2570), so a ratings model has
  little stable signal to exploit, and the season-to-season outcome
  mix swings far more than the fitted ratings can track (home-win
  rate 0.50 → 0.39 → 0.37 across 2022–2024). No rescue arm is
  proposed: the prereg allows none, and the failure is a property of
  the league's thin, high-variance data, not of a tunable arm.

## Defects found in verification (all non-material to this verdict)

1. The Phase A brief's cross-checks (written from the coordinator's
   first probe) counted 229 index rows as played matches. Eight 2022
   rows are unplayed scheduled fixtures (finished=false, scoreStr
   null, index score a `0-0` placeholder); the builder correctly
   excludes them under the frozen finished/non-cancelled rule, giving
   221 played matches and a 2022 season of 38, not 46. The brief's
   2022 levels were wrong accordingly (3.24 goals/match with the
   phantom 0-0s vs the true 3.92). All Phase A documents, the EDA
   JSONs, and the prereg carry the corrected numbers; the seed is
   thinner than briefed (38, not 46).
2. The brief's builder assertion about all-times event goal counts
   was wrong as worded: the all-times counts DO equal the recorded
   score on the two extra-time finals (the recorded score includes
   the ET goals) — only the 90-minute event counts differ. The
   builder asserts the corrected rule (90-minute mismatches exactly
   the two finals; all-times mismatches none).
3. Codex's first builder draft stored the recorded (ET-inclusive)
   score for the two extra-time finals (`recorded if et`), inverting
   the frozen 90-minute rule. Caught by the coordinator's review of
   the diff before any run; fixed to the event-derived ≤90-minute
   score (both finals 1-1). The committed CSV was verified: the two
   finals read 1-1.
4. Codex's `eda.py` as delivered had a syntax error (the `summary`
   dict literal was missing its closing brace). Fixed by the
   coordinator (one `}`); the script then ran clean and every EDA
   number was recomputed independently.
5. Codex's chat summary of the dev table transcribed the 2024
   climatology RPS as 0.242759785379; `results_dev.json` and the
   independent recompute from `results_dev.csv` agree on
   0.242759785073 (rounded 0.242760 above). A 3e-10 transcription
   slip, immaterial to every leg.
6. A naive grep for "2025"/"2026" in `results_dev.csv` flags four
   lines; all four are digit substrings inside probability decimals
   (e.g. lam_a 1.6409728063612954), not season labels — the season
   column contains only 2023/2024, confirmed by parsing the CSV.
7. `results_dev.csv` is per-match by design: 184 rows (92 × 2 arms)
   with lambdas and 1X2/OU/BTTS probabilities; every headline number
   above was recomputed from those rows by the coordinator through
   an independent path and matches to 6dp. A spot refit with the
   engine's own DC reproduced the stored probabilities exactly
   (max difference 0.0 on sampled rows).

## S/C/K/T

Not buildable, frozen in `prereg/PREREG_SCKT_NOT_BUILDABLE.md` before
any fitting: no SOT, corners, or total-shots target exists in any
season (stats 0/221, shotmaps present-but-empty 221/221); no
yellow-card target exists (no stats, no plain Yellow events). No dev,
no virgin read, no engine.

**Verdict: FAIL. Nothing ships. League complete: 0 pass / 1 fail / 4 not buildable.**
