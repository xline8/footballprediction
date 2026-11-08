# G-CLA goals engine

Goals-only Dixon-Coles engine for Chile Liga de Ascenso. The modelling
population is `finished=1 AND phase=regular`; play-off ties and unfinished
placeholders are excluded. Fits are season-blocked and expanding, with
half-life 270 and the production rho grid.

Arms are `gate_zero`, `shrink` (ratings for teams with fewer than six prior
in-league matches scaled by n/6), and `x2` (the parent CL-LigaDePrimera
preceding-season transplant, as defined in the preregistration). The frozen
halves presentation constant is 0.4273 / 0.5727.

Run `python3 run_g_cla.py dev` from this directory for development. The
virgin command is `python3 run_g_cla.py virgin`; it reads 2025 only after
Gate Zero passes dev. Authority: `../../prereg/PREREG_G_CLA.md`.
