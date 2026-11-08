# G-HU-NBI (goals) — VERDICT: FAIL (dev gate)

Pattern: goals-only Dixon–Coles (no xG/shotmap exists in this feed).
Primary line 2.5. Dev = expanding walk-forward 2022/23–2024/25 (n=594);
virgin 2025/2026 **deliberately NOT read** — no arm passed dev.

| arm | dev OU2.5 LL | dev 1X2 LL | base OU LL | naive OU LL |
|---|---|---|---|---|
| gate_zero | 0.7098 | 1.0589 | 0.6912* | 0.7282* |
| shrink | 0.7084 | 1.0586 | 0.6912* | 0.7282* |

*expanding prior-window climatology / trailing-10 as recorded in
engine/goals/results_dev.json (pooled gate flags: beats naive TRUE,
beats base rate FALSE for both arms).

Per-season OU sign (GZ vs base): 2022/23 0.6867 vs 0.7004 ✓;
2023/24 0.7336 vs 0.6801 ✗; 2024/25 0.7092 vs 0.6932 ✗.
Gate: pooled OU leg fails vs base rate and the sign leg fails → FAIL,
mechanically, both arms. The 1X2 leg (GZ 1.0589 vs climatology 1.0696)
passed but cannot rescue the OU leg. Nothing ships.
