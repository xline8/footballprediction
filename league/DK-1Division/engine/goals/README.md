# G-DK1 goals engine

Gate Zero: production Dixon-Coles pattern (dc.py, ported from the
DK-Superligaen/J1 engine), goals-only observation — no xG exists in this
league's feed. Fit per scored season on all matches before the season's
first date (expanding, season-blocked), hl=270, rho from the production
grid. Arms: gate_zero; shrink (arms.py adjusted_lambdas, ratings of
teams with <6 prior in-league matches scaled by n/6); x2 (mover
transplant defined in run_g_dk1.py: DC ratings from a fit on the parent
DK-Superligaen's preceding season blended for arriving teams with <12
DK1 training matches). Runner: run_g_dk1.py dev|virgin. Metrics: 1X2 LL,
RPS, OU2.5 LL vs pooled-prior climatology; virgin calibration on
home-win rate and OU2.5 over-rate. Prereg: ../../prereg/PREREG_G_DK1.md.
