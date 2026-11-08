# G-IS1 verdict — FAIL — virgin not read

Prereg: `prereg/PREREG_G_IS1.md`. Dev pooled n=543 (seasons 2022–2025).
Virgin 2026 (n=137, complete) was **NOT read** because Gate Zero failed
the dev gate; per the frozen rule the variants are moot and no arm ships.

## Dev pooled metrics

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---:|---:|---:|
| Gate Zero | 1.085780 | 0.243000 | 0.685037 |
| SHRINK | 1.085780 | 0.243000 | 0.685037 |
| X2 | 1.107163 | 0.246435 | 0.681374 |
| Climatology | 1.063502 | 0.236163 | 0.630089 |
| OU2.5 base rate (0.6814) | — | — | 0.625810 |

## Dev per season (1X2 LL / RPS / OU2.5 LL)

| Season | Gate Zero | SHRINK | X2 | Climatology 1X2 LL / RPS / OU LL |
|---|---|---|---|---|
| 2022 | 1.064249 / 0.245319 / 0.719068 | identical | identical | 1.017990 / 0.235049 / 0.642684 |
| 2023 | 1.062822 / 0.239592 / 0.661029 | identical | identical | 1.045390 / 0.236307 / 0.603907 |
| 2024 | 1.074051 / 0.220735 / 0.715221 | identical | 1.089112 / 0.223161 / 0.699097 | 1.115517 / 0.225078 / 0.675110 |
| 2025 | 1.141211 / 0.266437 / 0.646073 | identical | 1.210902 / 0.277625 / 0.647677 | 1.073452 / 0.248176 / 0.599115 |

Per-season climatology values are recomputed here from the match CSV by
the coordinator (pooled prior-season rates per target season); the pooled
climatology row above is the pooled score of those per-season predictions,
as in `results_dev.json`.

## Gate arithmetic

Dev gate (prereg): pooled dev 1X2 LL and RPS must beat climatology, and
OU2.5 LL must beat the base-rate baseline. Gate Zero fails all three
legs: 1X2 LL 1.085780 > 1.063502 (+0.0223), RPS 0.243000 > 0.236163
(+0.0068), OU2.5 LL 0.685037 > 0.625810 (+0.0592). The failure is
decisive, not marginal — the fitted model is worse than predicting the
pooled prior-season outcome rates on every leg. SHRINK is bit-identical
to Gate Zero (0 lambda differences in every dev season: with
season-blocked fits, teams have 0 or 22+ training matches, so the
min(1, count/6) factor is 0 for unseen teams — who already sit at the
league mean — and 1 for everyone else). X2 is worse than Gate Zero on
every metric and fails the per-season sign check in 2024 and 2025
(1.089112 > 1.074051; 1.210902 > 1.141211); it passes the sign check
under the prereg's at-least-half rule (2/4, on ties in 2022–2023), but
that is moot once Gate Zero fails dev.

## Diagnosis (descriptive, not a rescue)

- The worst dev season is 2025 (Gate Zero 1X2 LL 1.141211): 2025 is the
  one season where away wins (41.6%) outnumber home wins (38.7%), so a
  fitted home advantage actively hurts. Gate Zero beats climatology's
  1X2 LL in only one dev season (2024: 1.074051 vs 1.115517), and no
  season passes all three legs (2024 wins the 1X2/RPS legs but its
  OU2.5 LL 0.715221 is far above the base-rate baseline).
- X2's offsets all saturated at the preregistered clamp (±log 1.25 =
  ±0.2231) in both active seasons (2024: Besta att +0.2231 / con
  −0.2231, 2. Deild att −0.2231 / con +0.2231; same in 2025): the
  estimated mover effects exceeded the clamp in every case, and the
  full-strength shifts made 1X2 worse while barely improving OU2.5
  (0.681374 vs Gate Zero 0.685037, still far above the 0.625810
  baseline). The mover effect is real descriptively (F4) but the
  clamped full-strength application does not survive the gate.
- Same-origin entrant matches are unchanged by X2 by construction
  (att and con cancel: exp(+0.2231 − 0.2231) = 1); X2 differs from
  Gate Zero on 75 matches per active season (150 total at the 1e-12
  diagnostic threshold).

## Defects found in verification (all non-material to this verdict)

1. The harness's original `dev_gate.passes` folded the variant sign
   check in with an all-seasons rule, stricter than the prereg (dev
   gate = three metric legs only; sign check is virgin leg (iii) at
   at-least-half). Fixed before commit in `harness.py` (sign rule
   corrected to at-least-half, dev gate to the three metric legs);
   re-run reproduced every metric byte-identically except the two
   boolean fields. The verdict above applies the prereg's rule.
2. The coordinator's string comparison of CSV lambdas counted 155
   X2-vs-Gate-Zero differing matches vs the harness diagnostic's 150:
   the extra 5 are float noise (~1e-16) on same-origin entrant matches
   where att/con cancel. The harness's 1e-12 threshold is the honest
   count; the CSV values themselves are correct.
3. Codex wrote stray duplicate files at repo-root `engine/` and a
   stray `analysis/placeholder`; both removed before commit, no
   content lost (the league-tree copies are authoritative).
4. `results_dev.csv` is summary-free by design here: 1,629 per-match
   rows (543 × 3 arms) with lambdas and 1X2/OU/BTTS probabilities;
   every headline number above was recomputed from those rows by the
   coordinator through an independent path and matches to 6dp.

## S/C/K/T

Not buildable, frozen in `prereg/PREREG_SCKT_NOT_BUILDABLE.md` before
any fitting: no SOT, corners, or total-shots target exists in any
season (0/812 stats, 0/812 shotmaps); no yellow-card target exists
(no stats, no plain Yellow events). No dev, no virgin read, no engine.

**Verdict: FAIL. Nothing ships. League complete: 0 pass / 1 fail / 4 not buildable.**
