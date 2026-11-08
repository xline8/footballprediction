# K-HU-NBI (cards) — VERDICT: FAIL (dev gate)

Target: event-unified Yellow + YellowRed (the stats feed has NO cards
key in any row — events are the target by construction; plain Yellow
events occur in every season). Pattern: model_cards.py port, single
registered arm. Primary line 4.5. Dev n=594; virgin **NOT read**.

| arm | dev LL@4.5 | base LL | naive LL |
|---|---|---|---|
| gate_zero | 0.6907 | 0.6937 | 0.6879 |

Gate Zero beats the base rate pooled but LOSES to naive trailing-10
(0.6907 vs 0.6879) → dev gate FAIL, mechanically. Nothing ships.

Recorded deviation: the copied NO-OBOS cards runner also emitted an
x8 (referee) arm in dev. X8 was never a registered HU arm (FEATURES
drops it: virgin referee coverage is 18/198 = 9%); its output was
deleted before gating and plays no part in this verdict. Its dev LL
(0.6731, would have passed) is therefore moot under the frozen rule —
the same situation as NO-OBOSLigaen's K candidate. A future prereg
with a fresh virgin (2026/2027) is the only legitimate path for X8.
