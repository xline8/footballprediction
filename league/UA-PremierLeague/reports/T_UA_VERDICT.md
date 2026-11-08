# Verdict — T-UA (total shots): FAIL

Dev (valid stats n=462): A LL@14.5 0.6653, B 0.6664, C 0.6642 vs
base rate 0.6904, naive 0.6950 — all arms passed the dev gate.
Virgin (2025/2026, n=223, read ONCE; independently recomputed from
the virgin-season rows of predictions_virgin.csv, exact): A LL
0.7026 (cal +10.37pp), B 0.6918 (+8.56pp), C 0.7001 (+9.35pp);
SE ≈ 3.3pp, boundary ≈ 4.3pp — leg (ii) FAIL for every arm (B's
LL leg passed; calibration kills all three). The virgin season's
shot level jumped to 15.27/match after the feed-cold 2024/2025
(12.39) that dominates recent training weight. **FAIL — nothing
ships.** FT-only market. Provenance note: predictions_virgin.csv
also carries dev-season rows (harness export shape inherited from
the sibling engine); all gate metrics are computed on the virgin
season only and were verified as such.
