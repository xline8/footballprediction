# Pre-registration — G-KR (K League 1 goals)

Frozen 2026-11-09 before fitting. Reference: production Dixon-Coles + xG
blend. Dev 2021–2024 (912), virgin 2025 (228 complete), confirmatory 2026
(210 partial, reserved). Primary line OU 2.5; DEV over-rate 0.468.

Arms: Gate Zero (unmodified production pattern); SHRINK (teams with <6
prior K1 matches shrink attack/defence toward league mean); X2 mover arm
(K2-to-K1 ID-linked tier offset, only where prior K2 history exists). No
X3: it is DROPPED at r=0.283. X1 blend uses xG only where present, otherwise
goals-only. Baselines are pre-period climatology and goals climatology.

Dev gate: beat climatology on pooled 1X2 LL/RPS and beat the base-rate OU
LL. Virgin: LL <= Gate Zero and climatology; calibration for home-win and
OU over-rate; variant per-season sign check in at least half of dev seasons.
Calibration |breach| <=1pp is clean PASS, <=1 SE is PROVISIONAL PASS, else
FAIL. Both-pass selects lower virgin LL; ties prefer Gate Zero, then SHRINK,
then X2. If Gate Zero fails dev, virgin is not read. No fitted numbers are
present here.

Split rounds (>=34) are ordinary league matches with a phase flag; no phase
feature is used. Virgin is read once only after dev survival.
