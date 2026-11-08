# G-GR2 verdict

Preregistration: `prereg/PREREG_G_GR2.md`; calibration is
actual − predicted. **Virgin NOT read** (dev gate failed).

## Dev (scored 2022/2023–2024/2025, n=1,045)

| arm / baseline | LL 1X2 | RPS | OU2.5 LL |
|---|---:|---:|---:|
| Gate Zero pooled | 1.028463 | 0.211927 | 0.707253 |
| SHRINK pooled | 1.028463 | 0.211927 | 0.707253 |
| climatology pooled | 1.077632 | 0.231084 | 0.683044 |

Per-season Gate Zero model OU2.5 LL vs climatology: 2022/2023
0.728757 vs 0.689389; 2023/2024 0.681864 vs 0.675595; 2024/2025
0.708059 vs 0.683224 — the model's OU2.5 is worse in **every**
dev season while its 1X2 LL beats climatology by ~0.05 and its RPS
by ~0.02 in every season.

## Gate arithmetic

- Dev leg 1X2 LL: PASS (1.028463 < 1.077632).
- Dev leg RPS: PASS (0.211927 < 0.231084).
- Dev leg OU2.5 LL: **FAIL** — 0.707253 is not < base-rate
  0.683044. Gate Zero is dead; SHRINK is moot (and identical:
  SHRINK ≡ Gate Zero everywhere, the 1–5-match band never occurs
  under season-blocked fitting — 0 teams with 1–5 prior matches in
  every target season; the 7/6/5 unseen teams take a = d = 0 in
  both arms. The G-J2/GR finding again).
- The failure is a totals-shape failure, not a level failure:
  pooled mean predicted P(over 2.5) is 0.4066 against an actual
  over-rate of 0.4268 (gap +2.0pp), yet the per-match
  over-probabilities score worse than a constant — the DC ratings
  help pick winners (1X2/RPS pass) but their totals variation is
  noise for the OU2.5 line in this league. Same leg, same pattern
  as the parent tier: G-GR also failed its dev gate on OU2.5 LL.

G-GR2 verdict: **FAIL; nothing ships. Virgin deliberately NOT
read.** Prediction CSV: none. Fitted virgin params: none.

## Verification (independent of the Codex-built harness)

- `dc.py` and `arms.py` are byte-identical to the GR-SuperLeague
  engine; `harness.py` differs only in the league plumbing listed
  in the Codex brief (data file, seasons, xG=None, virgin filename,
  real fitted params on PASS, full virgin leg-(i) check).
- The coordinator re-ran the dev harness (identical numbers) and
  recomputed every per-season model and climatology figure with an
  independent driver (own train/target splits, own scoring) from
  `gr2_matches.csv`: all 12 model/climatology cells match the
  harness to <1e-9, and the pooled rows recompute exactly from the
  per-season rows. Loaded rows 1,591 (dev only); no 2025/2026 or
  2026/2027 row is read anywhere in the dev path.
- No virgin file exists under `engine/goals/` or `predictions/`.

## Non-buildable candidates (payload-level evidence)

- S-GR2 (SOT), C-GR2 (corners), K-GR2 (cards), T-GR2 (total shots):
  **not buildable** — `content.stats` is null and the shotmap is
  empty in all 1,935 payloads (builder-asserted); no referee is
  named in any payload; event cards are 337 in 1,935 matches with
  no stats feed to unify against. No dev or virgin evaluation was
  run for any of them, and none was preregistered.
