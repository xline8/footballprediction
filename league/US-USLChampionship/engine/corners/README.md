# USL corners engine

Port of the US-MLS corners engine against `data/usl_matches.csv`. Arms are
Gate Zero and X7; X7 uses the minimum-8 box-touch history rule and falls back
to Gate Zero when unavailable. Primary line is 9.5, ladder 8.5/9.5/10.5;
warm-up is 2021 and scoring is 2022–2024.

Run dev with `python3 run_c_usl.py dev`. Virgin is not run in Stage 2 and is
coordinator-gated.
