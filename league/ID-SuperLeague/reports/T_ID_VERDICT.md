# Verdict — T-ID (total shots): **NOT BUILDABLE**

No prereg was written and nothing was fitted for this candidate,
because the feasibility condition in the programme template fails —
twice over.

Evidence (Step 1, measured from payload content, not index flags):

1. **No virgin target.** `total_shots` exists only inside the stats
   era — 2021/2022 from 2022-01-13 (140/306), 2022/2023 complete
   (306/306), 2023/2024 until 2023-10-30 (153/314), 2024/2025 only 8
   scattered matches — and the virgin season 2025/2026 contains
   **zero** stats rows (0/306), as does 2026/2027 (0/80).
2. **The last era season is corrupt anyway.** In every 2023/2024
   stats payload, `total_shots` is an exact copy of `ShotsOnTarget`
   (100% of rows equal, corr 1.0, verified in raw JSON; values sit on
   the ~9-per-match SOT scale, not the 17–19 total-shots scale of
   2021/2022–2022/2023). Even the dev-era target is therefore only
   trustworthy for 2021/2022 (partial) and 2022/2023.

With no target in the virgin window there is no gate to run and no
virgin to read. **T-ID is NOT BUILDABLE and nothing ships.** If
FotMob restores this league's stats feed for a full recent season,
the candidate needs a fresh six-step pass over the new data; nothing
in this build pre-registers it.
