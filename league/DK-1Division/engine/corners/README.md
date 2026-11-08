# C-DK1 corners engine

Gate Zero: model_corners_v3 pattern (core.py, ported from
DK-Superligaen: decayed shot-rate factors + possession/big-chance
multiplier; gamma/r/beta fitted per season-block on prior data only).
X7: box-touch multiplier arm (core multiplier, z_bt). X5: trailing-rate
blend — mu = 0.5*mu_GZ + 0.5*trailing-10 naive total, GZ's r. Seed
2022/2023, scored dev 2023/2024-2024/2025, virgin 2025/2026. Primary
line 9.5. Note: the __base baseline is the ported core's own
decayed league-mu construction (stats_window at the season cutoff),
identical to the parent league's shipped engine. Runner:
run_c_dk1.py dev|virgin. Prereg: ../../prereg/PREREG_C_DK1.md.
