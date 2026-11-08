# Pre-registration — T-FI (FI-Veikkausliiga total-shots model): NOT BUILT

Frozen: 2026-11-10, before any fitting. Branch `build/fi-veikkausliiga`.

T-FI is **not built**, by feasibility, recorded here so the absence is an
auditable decision and not an omission:

- The `total_shots` target changes definition between the thin stats era
  and the rich stats era. Levels per match: 19.377 (2021), 16.898 (2022),
  15.940 (2023), 15.162 (2024) vs 26.395 (2025), 26.305 (2026), while SOT
  stays in its normal band (8.198–9.463) across the break. The thin-era
  series and the rich-era series are not the same quantity (implied
  on-target share ≈ 0.52 vs ≈ 0.35).
- The conveyor feasibility rule requires the target to exist AND a valid
  virgin window to contain it. The virgin (2026) does contain the
  rich-era target — but a dev gate can only validate an arm against the
  SAME quantity, and the rich-era quantity exists in exactly ONE dev
  season (2025, n = 177). One season cannot support the programme's
  season-blocked walk-forward dev protocol (warm-up + ≥3 scored seasons),
  and pooling thin-era dev rows would gate the arm on a different target
  than the one it would ship against.
- No arm, window, or line is therefore frozen, nothing is fitted, and
  the virgin is not read for total shots. If a future season adds a
  second rich-era dev season, T-FI can be pre-registered fresh at that
  point — it may not be rescued inside this prereg.
