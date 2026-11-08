# Pre-registration — K-KR (K League 1 unified yellows)

Frozen 2026-11-09 before fitting. Reference: production cards architecture.
The target is explicitly `yellow_home + yellow_away`, using event-feed
yellows when events exist and stats fallback otherwise. DEV agreement was
683 both-present, 630 equal, 53 disagree; events were larger in 47.
Dev 2021–2024 (912), virgin 2025 (228 complete), confirmatory 2026 (210
partial, reserved). Primary line OU 3.5; DEV over-rate 0.444.

Arms: Gate Zero; X8 referee strictness on named-referee matches, falling
back to Gate Zero for unknown or under-8 referee histories (named-match
reliability r=0.362). Baselines are league base rate at 3.5 and naive
trailing-10.

Dev gate: beat the base-rate and naive count baselines. Virgin: score no worse
than Gate Zero and calibration breach <=1pp clean PASS, <=1 SE PROVISIONAL
PASS, otherwise FAIL; variant also needs the per-season dev sign check in at
least half of dev seasons. Both-pass chooses the lower virgin score; ties go
to Gate Zero. If Gate Zero fails dev, virgin is not read. Split rounds >=34
are ordinary matches with phase flag only; no phase feature.
