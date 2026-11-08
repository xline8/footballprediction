# T-PY total-shots engine

Reads the PY CSV with lowercase total-shots fields, uses A/B/C shots-family arms, line ladder 23.5/24.5/25.5/26.5, and frozen 1H share 0.465. Seed is 2025 Apertura, dev is 2025 Clausura plus 2026 Apertura, and virgin is transitional 2026 Clausura.

```text
python3 league/KR-KLeague1/engine/total_shots/run_t_kr.py dev
python3 league/KR-KLeague1/engine/total_shots/run_t_kr.py virgin
```

The engine writes dev/virgin results and conditional fitted parameters; no arm passed the virgin calibration leg, so no prediction CSV was emitted.


