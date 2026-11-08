# Pre-registration — S-KR (K League 1 shots on target)

Frozen 2026-11-09 before fitting. Reference: production SOT architecture.
Dev 2021–2024 (912), virgin 2025 (228 complete), confirmatory 2026 (210
partial, reserved). Primary line OU 7.5; DEV over-rate 0.541.

Arms: Gate Zero; ratio-shrink with the production fixed prior; X4 trailing
xG/shot arm (r=0.701, shotmap-era guarded). X6 xGOT/shot is dropped because
its population is only ~0.33–0.35 of shots. Baselines are league base rate
at 7.5 and naive trailing-10.

Dev gate: beat the base-rate baseline on the reference SOT likelihood and
the naive count baseline on the preregistered score. Virgin: likelihood leg
<= Gate Zero and baseline, calibration |predicted over-rate - actual| <=1pp
clean PASS, <=1 SE PROVISIONAL PASS, otherwise FAIL. Both-pass chooses the
lower virgin score; ties prefer Gate Zero, then ratio-shrink, then X4.
Variants require the per-season dev sign check in at least half the seasons;
Gate Zero is exempt. If Gate Zero fails dev, virgin is not read.

Split rounds >=34 are ordinary matches with a phase flag and no phase
feature. Virgin is read once only after dev survival.
