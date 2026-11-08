# Step 6 — Model Design (SK-2Liga)

Windows (all candidates): training seed 2021/2022; dev =
walk-forward, season-blocked, evaluation seasons 2022/2023,
2023/2024, 2024/2025 (n = 613 finished matches: 200 + 231 + 182);
**virgin = 2025/2026 (n = 240 finished, complete), read ONCE,
only for arms passing the dev gate**. 2026/2027 is in progress
(rounds 1–16, 127 finished) and is NOT read in this build
(reserved confirmatory). Inclusion: finished matches only, no
phase rule (no phases exist). Calibration rule (programme-wide):
|breach| ≤ 1.0pp clean PASS; ≤ 1 SE PROVISIONAL; else FAIL. Gates
never move after results.

## Candidates

### G-SK2 — goals (Dixon–Coles, goals-only) — THE ONLY CANDIDATE
Reference: production `model_v2.py` DC pattern, hl = 270,
observation goals-only throughout (X1 dropped — no xG). Arms:
**Gate Zero**; **SHRINK** (sanctioned G-J2-lesson arm: ratings of
teams with <6 prior in-league matches shrunk `a *= n/6, d *= n/6`
at prediction time — expected to be near-identical to Gate Zero
here, since every returning club carries a full prior season of
matches and newcomers sit at n = 0, where both arms agree; the
arm is registered anyway and ties go to Gate Zero); **X2** (mover
tier offset, FEATURES X2: a relegated club's ratings shifted by
the cumulative mean ΔGF/ΔGA of transitions completed before the
target season, per EDA F4; ≡ Gate Zero for 2022/2023 where no
transition is completed). Primary metrics: 1X2 LL/RPS + OU2.5 LL
vs climatology.

### S-SK2 — shots on target: NOT BUILDABLE (no prereg, no virgin read)
No SOT data in any payload (no stats feed). There is no target to
fit, no dev window to gate on, and no virgin window to read.
Recorded as considered-and-rejected on data absence.
Verdict doc: `reports/S_SK2_VERDICT.md` (NOT BUILDABLE).

### C-SK2 — corners: NOT BUILDABLE (no prereg, no virgin read)
No corners data in any payload (no stats feed). Same reasoning
as S-SK2. Verdict doc: `reports/C_SK2_VERDICT.md` (NOT BUILDABLE).

### K-SK2 — cards: NOT BUILDABLE (no prereg, no virgin read)
No cards data in any payload (no stats feed; the event feed
carries goals and, in some blocks, red-card counts, but no
yellow-card series exists to target). Same reasoning as S-SK2.
Verdict doc: `reports/K_SK2_VERDICT.md` (NOT BUILDABLE).

### T-SK2 — total shots: NOT BUILDABLE (no prereg, no virgin read)
No shots data in any payload (no stats feed, no shotmap). Same
reasoning as S-SK2. Verdict doc: `reports/T_SK2_VERDICT.md`
(NOT BUILDABLE).

## Halves presentation

Goals: FT + 1H/2H via the frozen EDA F3 constant (0.4940),
presentation only, for the shipped market. All other markets:
FT-only by absence of data (no halves source exists for any of
them).
