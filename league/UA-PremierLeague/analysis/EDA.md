# Step 3 — EDA: UA-PremierLeague (numbers: eda_numbers.json)

Levels and home advantage: see Step 1 table. Home-win rate
0.375–0.441 across seasons; the war-era seasons sit at the low end.

Split-half trait reliabilities (seed 42, teams with ≥20 matches):
- Dev block (2022/2023–2024/2025; 21 teams): goals for r=0.773 /
  against 0.512; SOT for 0.948 / against 0.745; corners for 0.867 /
  against 0.633; total shots for 0.880 / against 0.727; possession
  for 0.873; EVENT yellows for 0.198 / against 0.095 — cards team
  traits are WEAK/NOISE at dev-block scale (the pooled all-era
  figure, 0.70/0.68, is carried by the excluded 2021/2022 season
  and longer careers; the honest dev-scale number is the weak one).
- Fit era incl. virgin (2022/2023–2025/2026): goals 0.858/0.721,
  SOT 0.807/0.773, corners 0.717/0.586, shots 0.808/0.869, event
  yellows 0.426/0.602.

Halves (event times, dev era 2022/2023–2024/2025 pooled): goals 1H
share 0.4441; cards 1H share 0.3290. Per-season goal shares
0.429–0.452, card shares 0.319–0.338 — league constants are the
only permitted halves mechanism (frozen-constant doctrine); SOT /
corners / total shots have no halves source at all → FT-only.

Referee: coverage 0/1,191 — no referee trait can be measured.
xG / box touches / big chances: absent — no reliability measurable.

Dev line scan (scored dev 2023/2024+2024/2025, valid stats n=462):
SOT over-rates 6.5: 0.4957, 7.5: 0.3766 → primary 6.5. Corners
8.5: ~0.517 → primary 8.5. Total shots 13.5: 0.5455, 14.5: 0.4827
→ primary 14.5. Event yellows (all dev rows n=480) 3.5: 0.6076,
4.5: 0.4262 → primary 4.5. Goals OU line 2.5 by convention.
