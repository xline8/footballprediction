# T-US-MLS total-shots engine

This engine implements `league/US-MLS/prereg/PREREG_T_US.md`, reading `league/US-MLS/data/us_matches.csv` with year season labels. Development loads 2021–2024; 2021 is warm-up, 2022 is tuning, and the gate pool is 2023 + 2024 (n=390). The primary line is 25.5 and the ladder is 24.5 / 25.5 / 26.5.

```bash
python3 league/US-MLS/engine/total_shots/run_t_j1.py dev
```

Arms A and C are evaluated. Virgin commands are reserved for the later stage. Presentation-only half ladders use the frozen 0.456 / 0.544 split.

