# G-RS goals engine

Dixon-Coles goals-only model for RS-SuperLiga (Serbia Super Liga,
FotMob 182), ported from the FI-Veikkausliiga reference engine
(`inbox-muse2/_shared/reference/FI-Veikkausliiga/engine/goals/`).
Prereg: `prereg/PREREG_G_RS.md` (frozen 2026-11-10, before any fitting).

```text
python3 run_g_rs.py dev
```

Outputs are `results_dev.json` and `results_dev.csv` in this directory.
There is NO virgin subcommand and NO virgin code path here: the virgin
run is a separate later step, only if the dev gate passes.

## Port notes

- `dc.py` is byte-for-byte identical to the FI reference (md5
  `bcf5e7e6de27e790bf85a1facb296e5d` on both files): 14 sweeps, damping
  0.7, +0.25 smoothing, home init 0.28, MAXG = 10, production tau,
  rho grid (0.0, −0.05, −0.10, −0.15) by goals log-likelihood, decay
  HL = 270 days. No constant changed.
- `arms.py` / `harness.py` are the FI files with only the RS adaptations
  below; `run_g_rs.py` mirrors `run_g_fi.py` with the `dev` subcommand
  only.

## RS adaptations (frozen in the prereg)

1. **Seasons are "YYYY/YYYY" strings.** The FI code did `int(season)`
   and `str(int(s) - 1)`; that arithmetic is meaningless here. All
   season arithmetic goes through the explicit `SEASON_ORDER` map in
   `arms.py` (`_prev_season()`). No integer parsing of season strings.
2. **Entrant identification uses the previous season's REGULAR-phase
   teams only.** The plain-absence rule catches the tier-2
   qualification opponents (FK Graficar, Indjija), who appear in
   qualification rows but never as regular members; the regular-phase
   rule removes them (EDA.md F4). Applies both to the completed
   entrant transitions (the offset's estimation sample) and to the
   entrants of the predicted season.
3. **Entrant transitions measured on league-member rows only**
   (`phase != "qualification"`), enforced in the loader.
4. **SHRINK unchanged from FI:** at prediction time a team with
   n < 6 prior in-league matches has its log-ratings scaled,
   `a *= n/6`, `d *= n/6`.
5. **Qualification rows excluded from fitting AND scoring** (8 rows:
   4 in the 2021/2022 seed, 4 in scored 2022/2023), enforced in
   `load()` itself. Awarded match 4271663 (2023/2024) IS fitted and
   scored (FT score authoritative).
6. **Goals-only:** `xgh` / `xga` are `None` always — the feed carries
   no xG columns in any season, so the DC fit uses the goals-only
   branch.
7. **Dev loader refuses the virgin/reserve seasons.** `run_dev()`
   passes `forbid={"2025/2026", "2026/2027"}`; `load()` rejects any
   caller asking for a forbidden season and asserts the returned rows
   contain none. Dev loads only 2021/2022–2024/2025; scored seasons
   2022/2023, 2023/2024, 2024/2025. (One port defect found and fixed
   during the build: the first version of the refusal raised on any
   forbidden-season row merely *present in the file*, which made dev
   unrunnable since the CSV contains those rows. The refusal now
   correctly means "never loaded", not "never present in the file".)
8. **Climatology baseline exactly as FI:** expanding prior-seasons
   pooled outcome rates + OU2.5 over-rate; pooled climatology is the
   pooled score of the per-season expanding climatology predictions.

## Dev results (2026-11-10 run)

Per-season n = 296 / 296 / 296 league-member rows, pooled n = 888.
Lower is better for all three metrics.

| Arm | Season | 1X2 LL (model / clim) | RPS (model / clim) | OU2.5 LL (model / clim) |
|---|---|---|---|---|
| gate_zero | 2022/2023 | 1.020821 / 1.070613 | 0.207540 / 0.230004 | 0.692730 / 0.693147 |
| gate_zero | 2023/2024 | 0.936981 / 1.047146 | 0.195898 / 0.233425 | 0.715397 / 0.699363 |
| gate_zero | 2024/2025 | 1.020988 / 1.074326 | 0.218217 / 0.237308 | 0.688544 / 0.694037 |
| gate_zero | **pooled** | **0.992930 / 1.064029** | **0.207218 / 0.233579** | **0.698890 / 0.695516** |
| shrink | pooled | 0.992930 / 1.064029 | 0.207218 / 0.233579 | 0.698890 / 0.695516 |
| x2 | 2024/2025 | 1.002767 / 1.074326 | 0.211904 / 0.237308 | 0.682115 / 0.694037 |
| x2 | **pooled** | **0.986856 / 1.064029** | **0.205114 / 0.233579** | **0.696747 / 0.695516** |

(X2 equals Gate Zero in 2022/2023 and 2023/2024 — the offset fires
first in 2024/2025, as preregistered: 0 completed transitions before
2022/2023, 2 before 2023/2024, 4 before 2024/2025. The 2024/2025
offset is GF −0.2855 / GA +0.2078 over the 4 prior transitions,
scoring multiplier clamped to 0.8, conceded multiplier 1.2309,
applied to OFK Beograd, Tekstilac Odzaci and Jedinstvo Ub. The
7-transition dev measurement recomputed from the same code path is
GF −0.3250 / GA +0.2425, matching EDA.md's −0.326 / +0.242.)

## Dev-gate reading — Gate Zero FAILS, verdict FAIL, virgin NOT read

Prereg gate (pooled dev): 1X2 LL and RPS must beat climatology AND
OU2.5 LL must beat the base-rate (climatology) baseline.

- Gate Zero pooled 1X2 LL 0.992930 < climatology 1.064029 — **PASS**
- Gate Zero pooled RPS 0.207218 < climatology 0.233579 — **PASS**
- Gate Zero pooled OU2.5 LL 0.698890 > climatology 0.695516 — **FAIL**
  (worse by 0.003374; driven by 2023/2024, 0.715397 vs 0.699363)

Gate Zero fails its dev gate on the OU leg, so per the prereg the
variants are moot, the G-RS verdict is FAIL, and the virgin
(2025/2026) is NOT read. For the record, X2 also fails the OU leg
pooled (0.696747 > 0.695516, worse by 0.001231) despite beating
climatology on LL and RPS, and SHRINK is identical to Gate Zero (see
below) — but neither fact changes anything: with Gate Zero dead, no
arm proceeds.

## Independent climatology recheck

The pooled climatology numbers were recomputed from
`data/rs_matches.csv` by a separate script (`/tmp/clim_recheck_rs.py`,
not importing this harness): per-season expanding prior-seasons rates
(2022/2023 train n=296, HW 0.432432 / DR 0.243243 / over 0.500000;
2023/2024 train n=592, over 0.472973; 2024/2025 train n=888, over
0.496622), pooled score over the 888 scored rows. Result:
LL 1.064029, RPS 0.233579, OU LL 0.695516 — identical to the harness
output to all six printed digits, per-season and pooled.

## Known quirk: SHRINK is numerically identical to Gate Zero

This is the FI SHRINK-numeric-identity quirk, and it recurs here
exactly. Verified: SHRINK equals Gate Zero to full float precision in
every season and pooled. Why, by construction: every incumbent has
≥ 30 prior in-league matches (factor min(1, n/6) = 1), and every
entrant has no fitted ratings at all (`a = d = 0` in the defaultdict,
so scaling by `n/6 = 0` leaves 0). SHRINK can only differ from Gate
Zero for a team with 1–5 prior in-league matches and non-zero fitted
ratings — a case this league's season structure (37 matches per team
per season) never produces in dev. No defect: the arm is implemented
as preregistered; the identity is a property of the data, not a bug.
