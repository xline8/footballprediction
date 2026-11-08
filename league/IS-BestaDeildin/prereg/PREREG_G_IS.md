# PREREG_G_IS — goals

Design authority: `analysis/MODEL_DESIGN.md`; X1 goals-only fallback and X2
in-corpus entrant are frozen. Seed 2021; dev 2022–2025, n=648; virgin 2026,
n=162. Primary metrics are OU2.5 LL plus 1X2 LL/RPS. The arms are Gate Zero
(DC goals-only, HR G pattern verbatim including rho grid and decay HL 270),
SHRINK, and X2.

The CSV dev over-rate at OU2.5 is 65.90%; home-win rate is reported in EDA.

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg: |mean predicted − actual| ≤ 1.0pp pooled for home-win rate and for OU2.5 over-rate, SEs reported; a breach within 1 SE of the boundary is recorded PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL ≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule. Both-pass rule: if Gate Zero and a variant both pass all legs, the lower pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes, G-IS verdict is FAIL and nothing ships.

Mechanical reading: an arm passes iff it survives the dev gate AND passes virgin legs (i)–(ii) (PROVISIONAL counts) AND, for variants, leg (iii); Gate Zero is exempt from (iii). Ties → simpler arm (Gate Zero, SHRINK, X2). If Gate Zero fails its dev gate, variants are moot, verdict FAIL, virgin NOT read.
