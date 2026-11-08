# Pre-registration — G-IQSL

Frozen 2026-11-10 before any fitting. Target: full-time home and away goals from the played-match CSV, regular phase only. Halves are presentation-only with frozen `goals_1h_share: 0.4323308271`, measured from event order before the HT marker in event-verified regular 2024/2025 matches.

Reference: production goals-only Dixon–Coles, half-life 270 days, rho grid `0, -0.05, -0.10, -0.15`, tau correction. Arms: Gate Zero (unmodified reference; unseen teams start at league mean) and SHRINK (Gate Zero plus ratings for teams with fewer than six prior in-league matches scaled by `n/6` toward the league mean). No X2 tier prior is used because the warehouse has no parent/sibling Iraq league.

Dev is season-blocked: seed 2021/2022; evaluate 2022/2023–2024/2025 on expanding regular history. Virgin is 2025/2026, read once only after dev gates pass. 2026/2027 is confirmatory, in progress, and unread for this verdict. Primary line is OU 2.5; pooled over-rate across the three scored dev seasons is 0.399 (440/1,104).

Calibration: `breach = mean predicted rate − actual rate (pp)`; `|breach| ≤ 1pp` is clean PASS, and a breach within 1 SE of the boundary is PROVISIONAL PASS.

## GATE LEGS (frozen)

Dev gate — pooled dev 1X2 LL + RPS must beat climatology and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Gate Zero failing dev ⇒ candidate FAILS, variants moot, virgin NOT read.

Virgin legs — (i) LL ≤ Gate Zero AND ≤ climatology; (ii) calibration `|breach| ≤ 1.0pp` pooled for home-win rate and OU2.5 over-rate with SEs, breach within 1 SE of the boundary = PROVISIONAL PASS, else FAIL; (iii) variant per-season sign check on dev. Both-pass rule: lower pooled virgin 1X2 LL ships; ties go to the simpler arm; none passes ⇒ FAIL, nothing ships. S/C/T/K have no preregistration because they are not candidates.
