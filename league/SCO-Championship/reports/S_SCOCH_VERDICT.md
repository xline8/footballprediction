# Verdict — S-SCOCH (Scotland Championship shots on target)

**FAIL at the virgin LL leg. Nothing ships.**

Prereg: `prereg/PREREG_S_SCOCH.md`. Primary line 7.5. Dev n=427
stats rows, virgin 2025/2026 n=177. All numbers recomputed by the
coordinator from the per-match prediction CSVs. Calibration =
predicted − actual.

## Dev (pooled LL@7.5; baselines: league 0.6978, naive 0.6786)

| Arm | Dev LL | Per-season sign vs GZ | Dev outcome |
|---|---|---|---|
| GZ | 0.6778 | — | PASS (beats both baselines) |
| RS | 0.6782 | 2/3 | PASS (beats both baselines) |

## Virgin (both arms read, per the frozen rule)

| Arm | Virgin LL@7.5 | Calibration | Legs |
|---|---|---|---|
| GZ | 0.69360 | +2.64pp, SE 3.77pp → PROVISIONAL | (i) FAIL |
| RS | 0.69382 | +2.57pp, SE 3.77pp → PROVISIONAL | (i) FAIL |
| league base rate | **0.69342** | −8.27pp | — |
| naive trailing-10 | 0.71017 | +1.01pp | — |

Leg (i) requires the arm's virgin LL ≤ Gate Zero's AND ≤ the best
baseline's. The best baseline is the league base rate at 0.69342;
GZ records 0.69360 — a failure by 0.00018, the thinnest margin in
this build, but the gate is mechanical and does not round. RS
(0.69382) also fails leg (i) and is worse than GZ. Calibration
(leg ii) is PROVISIONAL for both arms, and RS passes the dev sign
check (leg iii, 2/3) — none of that rescues leg (i).

**S-SCOCH is FAIL. Nothing ships** (no fitted params, no
predictions export). The virgin SOT level fell to 7.05/match from
the dev-era 7.7, and a flat prior-seasons base rate happened to
sit exactly on the virgin distribution; the v5 pattern's dev edge
(0.0008 over naive) was too thin to survive that shift.
