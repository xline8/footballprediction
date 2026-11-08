# USL shots-on-target engine

Port of the US-MLS v5 SOT engine using the complete stats-feed shot totals
and SOT columns in `data/usl_matches.csv`. Dev arms are `GZ` and `RS` only;
X4/X6 are excluded because USL has no shotmap inputs. Primary line is 8.5,
with ladder 7.5/8.5/9.5; warm-up is 2021 and scoring is 2022–2024.

Run dev with `python3 run_s_usl.py dev`. Virgin is not run in Stage 2 and is
coordinator-gated.
