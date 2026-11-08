# Preregistration — G-IS1

Frozen before fitting. Seed season is 2021. Development is season-blocked walk-forward over 2022, 2023, 2024 and 2025, n=543 (132+137+137+137). The virgin window is complete 2026, n=137. The dev harness must not read 2026 rows for fitting, selection, or gate setting.

The primary lines are 1X2 and OU2.5. The OU2.5 dev over-rate is frozen from the CSV at 0.6814. Climatology is pooled outcome rates and OU2.5 over-rate from seasons strictly before the target season; the virgin climatology is pooled 2021–2025.

Arms are limited to three: Gate Zero is the unmodified production Dixon–Coles goals-only reference, with movers at league mean. SHRINK shrinks ratings toward league mean by min(1, count/6), count being the team's training-window match count. X2 is SHRINK plus direction-specific mover offsets: entrants from Besta deildin (FotMob 215) receive the relegated offset, entrants from 2. Deild (FotMob 10226) receive the promoted offset. Each offset is estimated causally from completed transitions before the target season using in-corpus GF/GA deviations, keyed by team ID and previous-season tier membership in 216/215/10226, and clamped exactly to log(0.8)–log(1.25) per side. A club without an immediately preceding-season record in those leagues starts at league mean in every arm. Playoffs are included in fit and scoring.

The dev gate is: pooled dev 1X2 log loss and RPS must beat climatology, and OU2.5 log loss must beat the base-rate baseline at 0.6814. A variant must also pass the dev per-season sign check. Gate Zero is exempt from the variant sign check. Gate Zero failure makes variants moot and means the virgin is not read.

An arm passes only if it passes the dev gate and its virgin legs: (i) LL is no worse than Gate Zero and no worse than virgin climatology; (ii) pooled home-win rate and OU2.5 over-rate calibration error is at most 1.0 percentage point for a clean pass, or within 1 SE for a PROVISIONAL PASS, with SEs reported; (iii) variants pass their dev per-season sign check. Both-pass is required. A breach within 1 SE is PROVISIONAL PASS; otherwise FAIL, with the failed leg named mechanically. Ties go to the simpler arm: Gate Zero, then SHRINK, then X2. The virgin is read once only for arms passing dev.

