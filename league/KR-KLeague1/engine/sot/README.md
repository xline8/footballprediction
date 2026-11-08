# S-KR shots-on-target engine

Reads `data/kr_matches.csv` with target `ShotsOnTarget_home + ShotsOnTarget_away`. Dev uses 2021 warm-up and scores 2022–2024 at lines 7.5/8.5/9.5. Arms are GZ, RS, and X4; virgin is 2025 and conditional on the recorded gate.

```text
python3 league/KR-KLeague1/engine/sot/run_s_kr.py dev
python3 league/KR-KLeague1/engine/sot/run_s_kr.py virgin-metrics
```

Results are written here; virgin is deliberately unread because Gate Zero fails the 7.5 dev gate.
