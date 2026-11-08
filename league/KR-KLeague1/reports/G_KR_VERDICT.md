# G-KR verdict

Dev: 2021 seed; 2022–2024 scored, n=684. Gate Zero pooled LL/RPS = 1.073821/0.222732 versus climatology 1.088374/0.227424, but OU LL 0.698187 is worse than the available expanding climatology OU LL 0.691793 (the required base-rate leg). SHRINK is identical; X2 is 1.081105/0.224964/0.705805. Gate Zero fails the dev gate, so virgin was deliberately unread for every goals arm. Nothing ships.

Outputs: `engine/goals/results_dev.json` and `results_dev.csv`.

Disclosure (coordinator verification, 2026-11-09): the X2 arm as
implemented by the Codex port reuses the SE xG-multiplier construction
rather than a true K2 mover-offset — its dev numbers above are NOT a
valid test of the preregistered X2 and are recorded only for
transparency. The verdict does not depend on them: under the frozen
mechanical rule, Gate Zero's dev-gate failure ends the candidate and
the virgin stays unread for every arm. A valid X2 test would need a
new prereg and a fresh implementation.
