# Model design

G-AZ is the only candidate. S/C/T are not buildable because stats are None
and shotmap shots are empty in all 914 payloads. K is not buildable because
plain-Yellow events are zero in every season, named referees are 0/914, and
the only cards are rare Red/YellowRed events (154 total).

## G-AZ

The preregistered reference is the production Dixon–Coles goals-only pattern:
time-decayed expanding fits, fitted home advantage, and official FT goals.
The two arms are Gate Zero and SHRINK. SHRINK multiplies attack and defence
ratings by n/6 for teams with 1–5 prior in-league matches and leaves unseen
teams at the mean. EDA F13 finds zero teams in the 1–5 band at any target
season start, so the arms are expected to be identical; the verdict must check
the results file.

Training is season-blocked: 2021/2022 is the seed (112), evaluation is
2022/2023–2024/2025 pooled (540), and 2025/2026 is the complete virgin (198).
2026/2027 (64 through 2026-11-08) is a later confirmatory read only. Halves
use FT plus the frozen 0.4344 goals constant; no team or match halves model is
allowed.

No entrant arm is registered. The five real entrants show mean GF -0.45 and
GA +0.25, but there is no independent prior or sibling league.
