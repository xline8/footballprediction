# PA-LPF preprocessing

`data/build_data.py` filters index `league_id=9039`, resolves each JSON, and
emits finished, scored regular-season rows. It omits 76 errors and 45
final-stage rows (rounds `1/4`, `1/2`, `final`), retains the two awarded rows
with `excluded_awarded=True`, and uses official `header.status.scoreStr`.
The CSV has 690 rows; all analysis excludes the awarded rows, leaving 688.

Tournament labels are the payload labels `Apertura` and `Clausura`, kept
as labelled — with a naming flip across folders that the builder must
not "correct": in folders 2023–2025 Apertura runs Jan–May and Clausura
Jul–Nov, while in folder 2026 Clausura runs Jan–May and Apertura Jul–Nov
(verified in both `general.leagueName` and the infoBox Tournament name).
Modelling uses folder season + date order only, so the flip is a labelling
quirk, not a data defect; dates are UTC ISO dates and team identity is the
FotMob id. HT goals are non-shootout Goal events with `time <= 45`, including
45+stoppage events. `Half` HT events cross-check this. Empty event lists are
all verified 0–0 (66), so they receive HT 0–0. Penalty-shootout events are
not match goals. Red inventory counts `Red` and `YellowRed`; it is not a
target. The generated CSV is intentionally gitignored.
