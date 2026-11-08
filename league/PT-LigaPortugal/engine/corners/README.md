# C-PT repair

Season-blocked, date-grouped corner model. It uses HL-270 decay-weighted home and away corner rates, rolling-five shot for/against factors clamped to 0.6--1.7, and `mu = bh*(fhp*fac)^gamma + ba*(fap*fhc)^gamma`. Gamma is selected by full-count NB likelihood. Territorial features use the last ten valid matches and an eight-of-ten activation gate; Gate Zero uses possession/big chances and X7 uses opponent-box touches. League and trailing-10 baselines are independently computed. Moment variance is the plain training-window variance. `predictions_dev.csv` contains all arm/baseline rows and the runner validates grouped naive recomputation.

Virgin: NOT read (both arms failed the dev gate) — see the verdict.
