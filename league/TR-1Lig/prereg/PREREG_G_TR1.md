# Pre-registration — G-TR1 (TR-1Lig goals model)

Frozen: 2026-11-10, before any fitting. Design authority:
`analysis/MODEL_DESIGN.md`; features: `analysis/FEATURES.md`.

## Frozen scope and architecture

Fit only finished regular, non-awarded rows. Play-offs are excluded from all
fits and scores by the phase rule; awarded rows are excluded by the awarded
flag. Dev seed is 2021/22 and scored dev seasons are 2022/23–2024/25. Virgin
primary is 2025/26, read once only for arms passing the dev gate. 2026/27 is
reserved. No fitting or virgin read occurs in Phase A.

Gate Zero is the production Dixon–Coles pattern: 14 multiplicative sweeps,
damping 0.7, +0.25 smoothing, fitted home advantage, team attack/defence,
MAXG=10, production tau, rho grid (0, −0.05, −0.10, −0.15), and 270-day
half-life. xG is absent in the historical norm, so X1 is goals-only in
practice. SHRINK is the verbatim sanctioned arm: ratings for teams with fewer
than six prior in-league matches are multiplied by n/6. X2 is Gate Zero plus a
pre-season mover prior offset estimated inside the dev fit from the real
SüperLig CSV; only SüperLig↔1.Lig movers qualify. 2.Lig-promoted clubs are
unseen and use Gate Zero's league-mean rule.

## Dev gate and virgin legs

Dev gate — pooled dev 1X2 LL and RPS of an arm must beat climatology, and OU2.5
LL must beat the base-rate baseline, else the arm is dead. Virgin legs — (i)
LL leg: arm virgin 1X2 LL ≤ Gate Zero and ≤ climatology; (ii) calibration:
`|breach| ≤ 1pp` is clean, within 1 SE of the boundary is PROVISIONAL, beyond
it FAIL, for home-win rate and OU2.5 over-rate; (iii) variants must have arm
LL ≤ Gate Zero in at least half the dev seasons. Both-pass: lower pooled virgin
LL ships; one pass ships; tie goes to the simpler arm. If Gate Zero fails its
dev gate, variants are moot, verdict FAIL, virgin NOT read.

Mechanical reading: an arm must survive the dev gate and virgin legs (i)–(ii),
with (iii) for variants; PROVISIONAL counts as recorded. Primary lines come
from dev data; goals 1H presentation uses frozen 0.4482, while count markets
are not built.
