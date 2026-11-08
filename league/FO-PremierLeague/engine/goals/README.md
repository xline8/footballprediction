# G-FO goals engine

`run_g_fo.py dev` runs the frozen 2021 warm-up plus season-blocked 2022–2025 walk-forward. The awarded/excluded match is omitted from every fit and scored set. The dev harness returns only 2021–2025 rows and asserts that every fit cutoff is strictly before its target season.

The two arms are Gate Zero and the preregistered 0.85 attack/defence rating shrink. No virgin fit or prediction is implemented in Phase B.
