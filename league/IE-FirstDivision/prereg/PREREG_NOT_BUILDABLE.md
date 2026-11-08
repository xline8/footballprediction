# Pre-registration — NOT BUILDABLE: S-IEFD / C-IEFD / K-IEFD / T-IEFD

Frozen: 2026-11-10, in Phase A, **before any fitting**. Branch
`build/ie-first-division`. This record exists so that four candidate
markets are closed by measurement, not by omission — no engine is
built for any of them, no dev run is attempted, and no virgin read
is ever made for them.

Design authority: `league/IE-FirstDivision/analysis/MODEL_DESIGN.md`
§2; evidence per `league/IE-FirstDivision/analysis/DATA_UNDERSTANDING.md`
§3–§5, `EDA.md` F6, `FEATURES.md` §3 (R12–R19).

## The measurement (content, not index flags)

All 1,028 payloads (seasons 2021–2026, FotMob league 218) were read:

| Target | Source checked | Result |
|---|---|---|
| Shots on target (S-IEFD) | `content.stats.Periods` + `content.shotmap.shots` | Stats `Periods` is `None` in 1,028/1,028 matches; shot list is empty in 1,028/1,028. **No SOT target exists in any season.** |
| Corners (C-IEFD) | `content.stats.Periods` | Same: `None` in 1,028/1,028. **No corners target exists in any season.** |
| Total shots (T-IEFD) | `content.stats.Periods` + `content.shotmap.shots` | Same: no stats, empty shot list. **No total-shots target exists in any season.** |
| Yellow cards (K-IEFD) | `content.matchFacts.events` Card events + stats feed | Event feed lists Card events of type `Red` (142) and `YellowRed` (68) only — **zero plain `Yellow` events in 1,028 matches**. Stats feed is absent. No referee is ever named (`infoBox.Referee.text` is `''` in 1,028/1,028), so no referee arm could exist either. **No yellow target exists in any season.** |

## Why "not buildable" rather than "failed"

- The virgin window (2026) contains **no target for any of these
  four markets** — SOT 0/185, corners 0/185, total shots 0/185,
  yellows 0/185 (the 2026 Card events are Red/YellowRed only, 34
  total). A candidate that cannot be validated in its virgin window
  cannot be built, per the locked design rule (cf. C-J2 in the J.League
  design: "the J2 virgin window contains no corner targets at all, so
  the candidate could never be validated. Building it anyway would
  break the gate rule.").
- For K-IEFD specifically: the only card data is red-family events
  (210 total, 0.20/match). Reds alone are a rare-event count that the
  production cards design excludes as a target (FEATURES R12), and
  the sibling K-IE used event-*yellow* counts — a quantity this
  league's feed omits by provider design, exactly like J3's event
  feed omits yellows. Treating YellowRed second yellows (68 total,
  0.07/match) as a yellow target would be fabricating a target from a
  different event class.
- There is no era, window, or season in which any of these targets
  appears: the absence is flat across 2021–2026. Nothing is "coming"
  in a later pull that would change this verdict within this corpus.

## Consequences (frozen)

- No engine, no harness, no dev run, no virgin read, no predictions
  CSV, and no verdict file is produced for S-IEFD, C-IEFD, K-IEFD,
  or T-IEFD. Their absence from `engine/` is by design.
- If a future FotMob pull adds a stats feed or a yellow-card event
  stream for this league, these four candidates would need a new
  six-step pass (new DATA_UNDERSTANDING → new prereg) — this record
  must not be silently reopened.
- The league's only buildable candidate is G-IEFD
  (`prereg/PREREG_G_IEFD.md`). The league is complete when G-IEFD has
  passed through its gate (pass or fail) and this record is committed.
