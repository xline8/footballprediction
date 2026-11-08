# G-KR2 verdict — FAIL (dev gate, OU leg)

Dev pooled, scored 2022–2024, n=688 (seed 2021). Gate Zero (goals-only
Dixon-Coles; no xG exists in this league):

| leg | Gate Zero | climatology | pass |
|---|---:|---:|:--|
| 1X2 LL | 1.091030 | 1.095609 | yes |
| RPS | 0.230044 | 0.231682 | yes |
| OU 2.5 LL | 0.717872 | 0.694072 | **no** |

Gate Zero fails the dev gate on the OU leg, so under the frozen rule
the candidate FAILS and the virgin (2025) was deliberately NOT read
for any arm. Nothing ships.

Other arms (dev only): SHRINK is numerically identical to Gate Zero
(1.091030 / 0.230044 / 0.717872) — in a season-blocked fit every
returning team has ≥20 prior matches and every entering team sits at
the zero rating, which scaling by count/6 cannot move; the arm is
inert by construction here. X2 (true ID-linked K1 mover offset;
offsets hand-verified against the K1 corpus: Gwangju 2022
0.9158/1.1179, Seongnam 2023 0.8041/1.3355, Suwon Samsung 2024
0.7948/1.1634) scores 1.100290 / 0.233291 / 0.717238 — worse than
Gate Zero and worse than climatology on the 1X2 and RPS legs.

Disclosure — prereg scope ambiguity, moot: PREREG_G_KR2's operative
text requires a mover to have "no K2 matches before the target
season", which excludes Gimcheon Sangmu in 2023 (they played K2 in
2021 before their K1 season), while the same prereg names Gimcheon
in its in-scope list. A diagnostic run under the broader reading
(Gimcheon offset 0.9329/0.9812 applied) gives pooled
1.100425 / 0.233300 / 0.717863 — the arm fails under both readings,
so the verdict does not depend on the interpretation. A valid future
X2 test needs a new prereg either way.

Disclosure — implementation defects caught in audit before these
results: the first (Codex) port keyed mover offsets by team NAME
against an ID-keyed lookup (the arm silently never fired) and used
the mover's own matches as the league mean; both were rebuilt and
the shipped offsets above were recomputed by hand from the K1
corpus. Outputs: `engine/goals/results_dev.json`,
`engine/goals/predictions_dev.csv` (local). No virgin outputs exist.
