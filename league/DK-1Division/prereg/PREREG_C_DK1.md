# Pre-registration — C-DK1

Frozen 2026-11-10 before fitting. Target: full-time stats-feed total corners. Phase rule: rounds 1–22 regular; feed-labelled promotion/championship and relegation rounds 23–32 are ordinary rows. Halves use frozen `corners_1h_share: 0.469`, complete-splits era only. Target windows are 2022/2023–2025/2026; 2021/2022 is absent; virgin is 2025/2026 read once. Primary line: 9.5.

Gate Zero is `model_corners_v3.py`. Arms: X5 trailing corner rates and X7 trailing box touches. X9 is dropped for this feed. Dev is season-blocked 2022/2023–2024/2025; 2026/2027 reserved.

Calibration: `|breach| ≤1pp` clean PASS; `≤1 SE` PROVISIONAL; otherwise FAIL. Dev gate: pooled dev LL beats climatology/base-rate and naive trailing-10; Gate Zero failure makes variants moot and virgin unread. Virgin LL must beat or tie Gate Zero and climatology; calibration and variant per-season sign are required. Both-pass chooses the lower pooled virgin LL; ties go simpler.

GATE LEGS (frozen): Dev gate — pooled dev LL and primary-line LL of an arm must beat climatology/base-rate and naive trailing-10, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled, SE reported; within 1 SE is PROVISIONAL, beyond is FAIL; (iii) variants must have arm LL ≤ Gate Zero LL in at least half of dev seasons. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin LL ships; if only one passes, it ships; if none passes, C-DK1 FAIL and nothing ships. Virgin is read once.
