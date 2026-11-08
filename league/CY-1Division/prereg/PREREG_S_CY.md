# Pre-registration — S-CY (Cyprus 1. Division SOT)

Frozen: 2026-11-10, before any fitting. Target: total SOT, primary line 8.5 (dev over-rate 0.550, n=765), ladder 7.5/8.5/9.5. Arms: Gate Zero and RS, with BB prior 200 versus 20,000. Training seed 2021/2022; dev scored 2022/2023–2024/2025 n=765; virgin 2025/2026 read once only after a passing dev gate; confirmatory 2026/2027. FT-only: no period splits or event source. Calibration = actual − predicted.

## GATE LEGS

Dev gate — pooled dev LL@8.5 beats BOTH baselines (league base rate; naive trailing-10), else the arm is dead, no virgin read. Virgin legs — (i) LL@8.5 ≤ Gate Zero's AND ≤ best baseline's (Gate Zero: ≤ best baseline's); (ii) calibration |actual − mean P(over 8.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass (variant dev LL@8.5 ≤ Gate Zero's in ≥2 of 3 dev seasons). Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading: an arm passes iff it survives the dev gate AND passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such) AND, for the variant, leg (iii). Ties → simpler arm (Gate Zero before RS). Gate Zero dev failure ⇒ variants moot, FAIL, virgin NOT read.
