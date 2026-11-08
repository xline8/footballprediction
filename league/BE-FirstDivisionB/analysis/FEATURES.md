# Phase A — Features

The global pre-match causality and strict-before-kickoff rules apply.

- X1 — ADOPTED, goals-only. xG is absent throughout the dev era; production falls back to goals-only.
- X2 mover — ADOPTED. BE-A is the parent corpus. Mover magnitudes are descriptive and frozen from this league’s dev-era transition table; reserves and other new entrants are excluded.
- X3 set-play — DROPPED. xG/set-play is virgin-only.
- X4 xG/shot — DROPPED. Shotmap is virgin-only.
- X5 trailing target rate — NOT APPLICABLE to the goals candidate; count targets have no dev window.
- X6 xGOT — DROPPED. xGOT is virgin-only.
- X7 box touches — DROPPED. Stats feed is virgin-only.
- X8 referee — DROPPED. Referee identity is stats-era-only, and cards have no dev window.
- X9 territorial covariates — DROPPED. Stats-era-only.

Halves: adopt the dev-era event-time goals constant measured by eda_compute.py: 0.434014. Observed variance is 0.102295 versus a binomial noise floor of 0.109344, giving estimated true variance -0.007049. All count markets are FT-only by absence of a halves source in every dev window.

