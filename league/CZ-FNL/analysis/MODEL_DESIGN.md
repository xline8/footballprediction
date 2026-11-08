# Model Design

This brief stops before fitting. The training seed is 2021/2022. Development
is season-blocked walk-forward over 2022/2023, 2023/2024, and 2024/2025
(`n=720`). The complete virgin season is 2025/2026 (`n=240`) and is read once,
only for arms passing the dev gate. 2026/2027 (`n=111`, in progress) is
reserved confirmatory data and is never read by a harness in this build.

The programme calibration rule is frozen: absolute breach ≤1.0 percentage
point is clean PASS; ≤1 standard error is PROVISIONAL; otherwise FAIL.

## G-CZ-FNL — buildable

The sole candidate is the production Dixon–Coles goals-only pattern
(`model_v2.py`, `hl=270`). Arms are Gate Zero, SHRINK (the G-J2 lesson for
teams with fewer than six prior matches), and X2 (the relegated-mover offsets
listed in EDA, frozen before each target season). Gate Zero failure makes the
variants moot and leaves the virgin unread.

## Not buildable

S/C/T/K have no preregistration or virgin read in this build. S has no SOT in
any era; C has no corners in any era; T has no total-shots series in any era;
K cannot use event Yellows because plain Yellow is absent throughout the dev
era and appears only in the virgin season. There is no valid primary line for
these markets. Goals are FT-only for modelling, with the 1H constant used for
presentation only.
