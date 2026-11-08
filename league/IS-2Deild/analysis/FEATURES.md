# Features — IS-2Deild

Decisions are frozen for Phase B. All pre-match inputs use only matches strictly before kickoff; no current-match or post-match snapshot is eligible.

| Feature | Verdict | Reason |
|---|---|---|
| X1 goals observation | **ADOPTED** | Goals-only; any blend degrades to goals-only because xG is absent. |
| X2 source-specific mover prior | **ADOPTED** | Relegated-from-1.Deild and from-below priors are measurable in F4; effects are gated, never hard-coded. |
| X3–X4, X6–X7, X9 | **DROPPED** | No xG, shotmap, or stats feed. |
| X5 trailing target means | **DROPPED for S/C/K/T** | Targets are absent; the goals analogue is inside DC ratings. |
| X8 referee rate | **DROPPED** | Referee is empty in all 776 payloads. |

Rejected: R1 half-share modelling (F3 noise); R2/R3 finishing/conversion (no xG); R6 lineup/absence (no lineup data; no V10-style test claimed); R9 standings/H2H/table (leakage); R10 attendance (not pre-match); R12 red cards (rare and uncovered). Other unlisted features are ineligible. The 0.4418 first-half goal share is presentation-only.
