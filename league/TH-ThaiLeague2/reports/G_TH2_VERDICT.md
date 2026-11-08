# Verdict — G-TH2 (goals): **FAIL**

Prereg: `prereg/PREREG_G_TH2.md` (frozen and committed before fitting).
All numbers below were recomputed by the coordinator from the per-match
dev CSV against the league CSV (0 target mismatches).

## Dev (within-season walk-forward over 2024/2025 regular; warm-up 90, scored n = 183)

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | 1.0620 | 0.2232 | 0.7249 |
| SHRINK | 1.0620 | 0.2232 | 0.7249 |
| Climatology | 1.0478 | 0.2213 | 0.6961 |

## Gate arithmetic

Dev gate requires pooled 1X2 LL AND RPS to beat climatology AND OU2.5 LL
to beat the base-rate baseline. Gate Zero loses **all three legs**:
1X2 LL 1.0620 > 1.0478, RPS 0.2232 > 0.2213, OU2.5 LL 0.7249 > 0.6961.
Gate Zero therefore fails its own dev gate; per the prereg, variants are
moot and the **virgin was NOT read** (the harness refuses the virgin run
and no virgin artifact exists).

SHRINK note (recorded finding): SHRINK's predictions are row-for-row
identical to Gate Zero's on all 183 scored rows. The scored block begins
after a 90-match warm-up in which every active club already has 10–12
in-league matches, so the 1–5 prior-match band the arm addresses never
occurs at prediction time; the one thin-history club (Samut Prakan City,
1 match) withdrew inside the warm-up and never plays again. The X2 mover
evidence (n = 3 relegated clubs, mixed gaps) stands as measured; the arm
simply has no scored case to act on under this protocol.

Context: with a single pre-virgin season, the DC fit has at most 272
prior matches and as few as 90 at the start of the scored block; the
expanding climatology — which pools the same matches without team
ratings — beats it on every metric. The parent league's G-TH failed its
dev gate too (on the OU leg), with ten times the training data.

**G-TH2 FAILS. Nothing ships.** 2025/2026 remains unread for this
candidate; 2026/2027 remains the untouched confirmatory window.
