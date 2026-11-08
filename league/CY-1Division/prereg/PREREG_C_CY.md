# Pre-registration — C-CY (Cyprus 1. Division corners)

Frozen: 2026-11-10, before any fitting. Target: total corners, primary line 9.5 (dev over-rate 0.452, n=765), ladder 8.5/9.5/10.5. Arms: Gate Zero only, possession-only X9; `big_chance` and box touches are absent. Training seed 2021/2022; dev scored 2022/2023–2024/2025 n=765; virgin 2025/2026 once after dev pass; confirmatory 2026/2027. FT-only. Calibration = actual − predicted.

## GATE LEGS

Dev gate — pooled dev LL@9.5 beats BOTH baselines (league base rate; naive trailing-10), else the arm is dead, no virgin read. Virgin legs — (i) LL@9.5 ≤ Gate Zero's AND ≤ best baseline's (Gate Zero: ≤ best baseline's); (ii) calibration |actual − mean P(over 9.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass (variant dev LL@9.5 ≤ Gate Zero's in ≥2 of 3 dev seasons). Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading: an arm passes iff it survives the dev gate AND passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such) AND, for the variant, leg (iii). Ties → simpler arm (Gate Zero before POSS). Gate Zero dev failure ⇒ variants moot, FAIL, virgin NOT read.
