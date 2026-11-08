# Model design — Phase A freeze

No models are fitted in Phase A. G-DK2 is the only candidate. S-DK2, C-DK2, K-DK2, and T-DK2 are not candidates: their targets do not exist in any season, including the virgin window (stats null/empty shells, shotmap 0 shots, event cards reds-only at about 0.1/match). There is no virgin read for them because there is nothing to read.

| Candidate | Gate Zero | Arms | Status |
|---|---|---|---|
| G-DK2 | production Dixon–Coles goals-only pattern; HALF_LIFE 270, rho grid, goals-only fallback | gate_zero; SHRINK for teams with <6 prior in-league matches; X2 mover transplant | buildable |

X2 applies when a team has <12 in-league training matches and ≥10 parent-tier matches in the parent's immediately preceding season. Blend DC ratings toward a parent-tier DC fit with `w=(12−n)/12 × min(1,n_parent/20)`. No offset constant is hard-coded: the transplanted ratings come from the parent-tier fit under this frozen weight formula.

Windows: seed 2021/2022; dev 2022/2023–2024/2025 (576 matches); virgin 2025/2026 (192), read once only after Gate Zero passes dev; 2026/2027 transitional (90, rounds 1–15), never read for verdicts. Primary line is OU 2.5; dev mean total is (566+572+487)/576 = 2.819. Halves are presentation only via frozen 0.4611.
