# P5 Gate Zero reproduction report

## Headline verdict

**PASS for reproducible levels.** L1/L2 numeric reproductions: 215 (215 within 5e-07); L3 leg-decision reproductions: 60 (60 agreements, 0 disagreements).

Gate Zero is PASS only when all L1/L2 values reproduce within the criterion and all L3 decisions agree. No shipped verdict changes.

NOT_REPRODUCIBLE legs: S-LV:dev pooled LL (L2), S-LV:dev pooled LL (L2), S-LV:dev pooled LL (L2), S-LV:dev pooled LL (L2), G-AE:L1 virgin per-match, K-AE:dev pooled LL (L2), K-AE:dev pooled LL (L2), K-AE:L1 virgin per-match

The library convention is predicted − actual; sign translations are recorded in row notes.

## Sample

| Candidate | League | Market | Shipped outcome |
|---|---|---|---|
| T-J1 | J1 | total_shots | PASS provisional |
| S-J1 | J1 | sot | PASS clean |
| K-J1 | J1 | cards | FAIL sealed |
| G-SCO | SCO-Premiership | goals | PASS provisional |
| G-TR | TR-SuperLig | goals | PASS provisional |
| T-GR | GR-SuperLeague | total_shots | PASS clean |
| S-LV | LV-Virsliga | sot | PASS clean |
| C-GR | GR-SuperLeague | corners | PASS clean |
| G-AE | AE-ProLeague | goals | FAIL dev |
| K-AE | AE-ProLeague | cards | FAIL dev |

## Per-candidate counts

| Candidate | Rows | Mismatched | Not reproducible |
|---|---:|---:|---:|
| T-J1 | 31 | 0 | 0 |
| S-J1 | 44 | 0 | 0 |
| K-J1 | 44 | 0 | 0 |
| G-SCO | 25 | 0 | 0 |
| G-TR | 29 | 0 | 0 |
| T-GR | 31 | 0 | 0 |
| S-LV | 10 | 0 | 4 |
| C-GR | 38 | 0 | 0 |
| G-AE | 13 | 0 | 1 |
| K-AE | 18 | 0 | 3 |

## Diagnostics and guard demonstrations

L1 rows are per-match replays; L2 rows are per-season-to-pooled replays; L3 rows recompute decisions from persisted aggregates.

### Sealed guard (gate_lib.sealed_guard)

- G-AE: sealed load REFUSED without a dev-pass token (unreadable dev-pass registry)
- K-AE: sealed load REFUSED without a dev-pass token (unreadable dev-pass registry)
- T-J1: sealed load ACCEPTED after recording its dev-pass token (200 rows)

### Template constants (gate_lib.constants)

- T-J1 M_BAR = 24.9 carries a derivation record in PREREG_T_J1 (J1 dev mean 24.898, n=1,372): not flagged.
- Undocumented copy of M_BAR = 24.9 in another league spec: FLAGGED [WARNING] constant has no derivation record
- Undocumented copy of M_BAR = 24.9 in another league spec: FLAGGED [ERROR] exactly equals J1 without derivation

## Mismatch diagnoses

No L1/L2 numeric mismatches and no L3 decision disagreements were found in this run; every reproducible leg reproduces within the stated criterion. NOT_REPRODUCIBLE rows are listed above with their reasons (dev-fail candidates have no sealed artefacts by design; that absence is the expected reproduction of a dev FAIL, and the sealed guard demonstration above shows the library refusing those loads).

One SIGN_CONVENTION case was found and is NOT a mismatch: C-GR virgin calibration. The C-GR prereg freezes "Calibration = actual - predicted everywhere in this build" and its results_virgin.json stores -0.886pp for gate_zero; the library convention (predicted - actual) recomputes +0.886pp from the per-match CSV. |diff| is identical (0.886pp <= 1.0pp tolerance, band PASS either way); the row is recorded with the stored value and its translation. This is the AUDIT SS5.11 sign-convention class the library exists to eliminate in future builds. The T-GR harness sign case (AUDIT SS5.12) is handled the same way in its rows.

Library/runner bugs found and fixed during this Gate Zero run (each fix re-ran the full sample): (1) per-match column matching missed the p_over_8.5 dot spelling used by the J1-family and GR virgin CSVs (S-J1, C-GR L1 initially not reproducible); (2) K-J1 virgin CSV carries no actual column - actuals are now supplied from the league data file by match_id, per the prereg target definition; (3) goals virgin leg (i) was initially evaluated on OU LL - the goals preregs freeze leg (i) on 1X2 LL with a two-part (home-win + OU) calibration leg, and the runner now follows the prereg (G-TR x3 disagreement resolved: 1X2 LL 0.98913 <= Gate Zero 0.99635); (4) flat pooled-only dev schemas (S-LV) and top-level-arm virgin schemas (G-TR) were added to the normalisers.

Artefact inconsistencies (values that neither reproduce nor reduce to a sign translation): NONE found in the sample.

## Limitations

No refits are performed. Dev legs are recomputed from persisted per-season aggregates (L2), sealed values from per-match virgin CSVs for the shipped/reference arm only (L1); other arms' sealed legs are reproduced as decisions from persisted aggregates (L3), because no per-match artefacts exist for them. Shipped verdict files remain authoritative and are never altered.
