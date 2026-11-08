# Pre-registration — K-CY (Cyprus 1. Division cards)

Frozen: 2026-11-10, before any fitting. Target: event-unified yellows = Yellow + YellowRed, primary line 4.5 (dev over-rate 0.506, n=776), ladder 3.5/4.5/5.5. Stats has no yellow key; cards_source is events. Arms: Gate Zero only, because referee is empty and X8 is unavailable. Training seed 2021/2022; dev scored 2022/2023–2024/2025 n=776; virgin 2025/2026 once after dev pass; confirmatory 2026/2027. Half presentation constant is 0.3693. Calibration = actual − predicted.

## GATE LEGS

Dev gate — pooled dev LL@4.5 beats BOTH baselines (league base rate; naive trailing-10), else the arm is dead, no virgin read. Virgin legs — (i) LL@4.5 ≤ Gate Zero's AND ≤ best baseline's (Gate Zero: ≤ best baseline's); (ii) calibration |actual − mean P(over 4.5)| ≤ 1.0pp, SE reported, breach within 1 SE = PROVISIONAL PASS; (iii) dev per-season sign check for both-pass (variant dev LL@4.5 ≤ Gate Zero's in ≥2 of 3 dev seasons). Both-pass: both → lower pooled virgin LL ships; one → ships; none → FAIL.

Mechanical reading: an arm passes iff it survives the dev gate AND passes virgin legs (i)–(ii) (PROVISIONAL counts, recorded as such) AND, for the variant, leg (iii). Ties → simpler arm (Gate Zero before X8). Gate Zero dev failure ⇒ variants moot, FAIL, virgin NOT read.
