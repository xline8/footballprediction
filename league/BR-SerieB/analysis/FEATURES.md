# Phase 3.5 — Feature Engineering (X1–X9, judged in Série B)

| feature | verdict | evidence |
|---|---|---|
| X1 goals+xG blend | adopted as reference, goals-only in effect | xG absent from all dev seasons and from the virgin fit window; true blend exists only in 2025+ |
| X2 mover offset | **ADOPTED** | four ex-A and four ex-C movers each transition; two-sided offsets are fit inside dev |
| X3 set-play xG | **DROPPED** | measurable only in virgin/confirmatory era |
| X4 xG/shot | **DROPPED** | 2025+ only; cannot be exercised in dev |
| X5 trailing means | **ADOPTED** | shots r=.543; SOT=.395; corners=.406; valid cards=.262 |
| X6 xGOT | **DROPPED** | era rule; no dev exercise |
| X7 box touches | **ADOPTED if min-8 gate passes** | coverage 27%, 28%, 64%, 100%, 100%, 100%; r=.586 |
| X8 referee | **ADOPTED if gate passes** | 2021 zero coverage, scored dev coverage 94.7/93.7/76.6%; r=.397 |
| X9 covariates | **Gate Zero pattern** | use only if reliability and dev gate hold |

The goals SHRINK arm is sanctioned and included because eight mover teams per
season create the largest thin-data exposure in the program. Half shares are
constants, never team traits; missing arms remain inactive rather than being
imputed. Lineups, standings snapshots, H2H, and red cards are excluded.
