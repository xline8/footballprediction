# K-ITB cards engine

Reads the IT-SerieB CSV (unified target = event-feed yellows,
`yellow_home/yellow_away` with cards_source='events'). Gate Zero
only — the X8 referee arm was dropped in FEATURES (split-half
r = 0.061); the referee state in the model is carried but never
applied for Gate Zero. Run
`python3 league/IT-SerieB/engine/cards/run_k_itb.py dev`, then
`virgin`. Prereg: `PREREG_K_ITB.md`; primary line 4.5 and halves
constant 0.3733. Calibration in results = actual − predicted.
