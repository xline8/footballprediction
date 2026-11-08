# Model design

G-BD is the only candidate. S/C/T are not buildable because stats are None
and shotmap shots are empty in all 394 payloads. K is not buildable because
plain-Yellow events are zero in every season, named referees are 0/365 in dev,
and the only cards are rare Red/YellowRed events (59 total).

## G-BD

The preregistered reference is the production Dixon–Coles goals-only pattern:
time-decayed expanding fits, fitted home advantage, and official FT goals.
The two arms are Gate Zero and SHRINK. SHRINK multiplies attack and defence
ratings by n/6 for teams with 1–5 prior in-league matches and leaves unseen
teams at the mean. EDA F13 finds zero teams in the 1–5 band at any target
season start, so the arms are expected to be identical; the verdict must check
the results file.

Training is season-blocked: 2022/2023 is the seed (95, incomplete — rounds
4–22 only), evaluation is 2023/2024–2025/2026 pooled (270), and 2026/2027 is
the in-progress TRANSITIONAL virgin (29 through 2026-10-24). The season-end
2026/2027 read, when the season completes, is the confirmatory read. Halves
use FT plus the frozen 0.4217 goals constant; no team or match halves model is
allowed.

No entrant arm is registered. The five real entrants show mean GF −0.49 and
GA +0.93, but there is no independent prior or sibling league. The thin dev
windows (F14) are recorded honestly: the pooled gate is the decision unit.
