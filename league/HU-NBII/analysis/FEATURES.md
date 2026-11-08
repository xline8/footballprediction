# Feature decision — HU-NBII

The J1 definitions are the reference contract. Every candidate is dropped;
MODEL_DESIGN may use nothing.

| feature | decision | reliability / reason |
|---|---|---|
| X1 goals + xG observation pair | DROPPED | no xG/stats in 344/344; goals have no gateable window |
| X2 mover tier offset | DROPPED | three relevant movers, no window; measurable in principle but moot |
| X3 set-play xG share/rate | DROPPED | stats/xG absent 344/344 |
| X4 xG per shot | DROPPED | shotmap shots empty 344/344 |
| X5 trailing target-rate means | DROPPED | no target window; split-half GF r=0.075/0.186 and team n is small |
| X6 attacking xGOT per shot | DROPPED | shotmap/stats absent 344/344 |
| X7 opponent-box touches | DROPPED | stats absent 344/344 |
| X8 referee yellow rate | DROPPED | referee blank 344/344; only 47 card events total |
| X9 territorial corners covariates | DROPPED | corner/stat source absent 344/344 |

No halves constants are frozen. No feature is consumed by the model design.
