# Pre-registration — G-DK1

Frozen 2026-11-10 before fitting. Target: full-time total goals and 1X2 from `home_goals`/`away_goals`, goals-only because expected_goals is absent everywhere. Cards are not this target. Rounds 1–22 are `regular`; feed-labelled promotion/championship and relegation rounds 23–32 are ordinary rows with a phase flag. Halves are presented with frozen `goals_1h_share: 0.436` from events on 2023/2024–2025/2026; no team half feature.

Reference is production Dixon–Coles goals-only. Arms: Gate Zero; SHRINK for teams with fewer than six prior in-league matches; X2 mover offset, estimated only from prior-tier observations and only when causally available. X1 and X3 are dropped.

Dev is season-blocked: seed 2021/2022, evaluate 2022/2023–2024/2025. Virgin is 2025/2026, read once only after dev gates pass. 2026/2027 is reserved and unread. Primary line is OU 2.5, the nearest standard line to the dev distribution.

Calibration: `|breach| ≤1pp` is clean PASS; `≤1 SE` is PROVISIONAL; otherwise FAIL. Dev gate: pooled dev LL beats climatology/base-rate and naive trailing-10 where required; Gate Zero failing dev means candidate FAIL, variants moot, virgin not read. Virgin LL must beat or tie Gate Zero and climatology, calibration must pass, and variants need the per-season sign check. Both-pass rule selects the lower pooled virgin LL; ties go to the simpler arm. Virgin is read once.

GATE LEGS (frozen): Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-DK1 verdict is FAIL and nothing ships.
