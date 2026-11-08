# S-HU-NBI (SOT) — VERDICT: FAIL (dev gate, sign leg)

Pattern: model_sot.py v5 port. Primary line 8.5. Dev n=588;
virgin 2025/2026 **deliberately NOT read** — no arm passed dev.

| arm | dev LL@8.5 | base LL | naive LL |
|---|---|---|---|
| gate_zero | 0.6944 | 0.7175 | 0.7057 |
| rs | 0.6938 | 0.7175 | 0.7057 |

Pooled: both arms beat BOTH baselines. Per-season sign vs base rate:
GZ 0.6959/0.6899/0.6973 vs base 0.7466/0.7100/0.6956 — the 2024/25
season fails by +0.0017 LL (RS identical there, 0.6973). The frozen
sign leg requires improvement in EVERY dev season → FAIL for both
arms, mechanically. A genuine near-miss; no rescue arm exists under
this prereg. Nothing ships.
