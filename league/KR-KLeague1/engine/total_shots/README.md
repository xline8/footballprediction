# T-KR total-shots engine

Reads `data/kr_matches.csv`, uses A/B/C shots-family arms, line ladder 22.5/23.5/24.5, and frozen 1H share 0.418. Dev uses 2021 seed and scores 2022–2024; virgin is 2025.

```text
python3 league/KR-KLeague1/engine/total_shots/run_t_kr.py dev
python3 league/KR-KLeague1/engine/total_shots/run_t_kr.py virgin
```

The engine writes dev/virgin results and conditional fitted parameters; no arm passed the virgin calibration leg, so no prediction CSV was emitted.
