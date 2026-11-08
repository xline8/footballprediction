"""Data loading, walk-forward evaluation, and outputs — G-RS, DEV ONLY.

Port of the FI-Veikkausliiga reference ``harness.py``, with the RS
adaptations listed below. Everything not listed here is verbatim FI
behaviour. There is deliberately NO virgin code path in this file: no
``virgin_metrics``, no predictions writer. The virgin run is a separate
later step, only if the dev gate passes.

RS adaptations (frozen in PREREG_G_RS.md):
- Loads ``data/rs_matches.csv`` (no xG columns exist in this feed).
- Excludes ``phase == "qualification"`` rows from BOTH fitting and
  scoring (8 rows: 4 in the 2021/2022 seed, 4 in scored 2022/2023).
  The exclusion is enforced in ``load()`` itself, so no downstream
  function can ever see a qualification row.
- Goals-only: ``xgh`` / ``xga`` are set to ``None`` always, so the DC
  fit uses the goals-only branch (``oh, oa = yh, ya``).
- Dev mode loads ONLY seasons 2021/2022–2024/2025. The loader REFUSES
  2025/2026 and 2026/2027 rows in dev mode: ``run_dev()`` passes
  ``forbid={"2025/2026", "2026/2027"}`` and ``load()`` rejects any caller
  that asks for a forbidden season and asserts the returned rows contain
  none of them; forbidden rows present in the file are skipped by the
  allowed filter and never loaded. Scored seasons: 2022/2023, 2023/2024, 2024/2025.
- Season labels are "YYYY/YYYY" strings throughout; ``run_dev()``
  asserts the per-season scored n (296 league-member rows each, 888
  pooled) so a silent data change fails loudly instead of shifting
  the gate numbers.
- Rows carry their ``phase`` through to the arms module, which needs
  it for the regular-phase entrant rule (see ``arms.py``).
- Climatology baseline exactly as FI: expanding prior-seasons pooled
  outcome rates + OU2.5 over-rate; pooled climatology is the pooled
  score of the per-season expanding climatology predictions.
"""
import csv, json, math
from collections import Counter
from datetime import date
from pathlib import Path
from dc import DC
from arms import x2_multipliers, adjusted_lambdas, match_counts

ROOT = Path(__file__).resolve().parents[2]
SE = ROOT / "data" / "rs_matches.csv"
OUT = Path(__file__).resolve().parent

DEV_SEASONS = ("2021/2022", "2022/2023", "2023/2024", "2024/2025")
SCORED_SEASONS = ("2022/2023", "2023/2024", "2024/2025")
# Dev mode must never see these seasons. The loader refuses them
# (AssertionError) rather than filtering them silently.
FORBIDDEN_DEV = {"2025/2026", "2026/2027"}
EXPECTED_SCORED_N = 296  # league-member rows per scored season (300 - 4 qualification in 2022/2023; 296 in the others)


def load(path, allowed=None, forbid=None):
    # Dev mode refuses to load the forbidden seasons: a caller that asks
    # for one is rejected outright, and the returned rows are asserted
    # free of them. Forbidden rows present in the file are skipped by the
    # allowed filter, never loaded.
    if forbid is not None and allowed is not None and set(allowed) & set(forbid):
        raise AssertionError(f"dev loader refuses to load seasons {sorted(set(allowed) & set(forbid))}")
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if allowed is not None and r["season"] not in allowed: continue
            if r["phase"] == "qualification": continue  # cross-tier rows: excluded from fitting AND scoring
            rows.append({"match_id": int(r["match_id"]), "season": r["season"], "phase": r["phase"],
                         "date": date.fromisoformat(r["date"]),
                         "hi": int(r["home_team_id"]), "ai": int(r["away_team_id"]), "home": r["home_team"], "away": r["away_team"],
                         "yh": int(r["home_goals"]), "ya": int(r["away_goals"]),
                         "xgh": None, "xga": None})
    if forbid is not None:
        assert not any(r["season"] in forbid for r in rows), "dev loader loaded a forbidden season"
    return sorted(rows, key=lambda r: (r["date"], r["match_id"]))


def _fit_predict(train, target, arm):
    cutoff = min(r["date"] for r in target)
    model = DC().fit([r for r in train if r["date"] < cutoff], cutoff)
    movers = set()
    mult = x2_multipliers([r for r in train if r["date"] < cutoff], target) if arm == "x2" else {}
    return model, movers, mult, match_counts([r for r in train if r["date"] < cutoff])


def _scores(rows, probs):
    ll = rps = oull = 0.0
    for r, p in zip(rows, probs):
        y = (1, 0, 0) if r["yh"] > r["ya"] else ((0, 1, 0) if r["yh"] == r["ya"] else (0, 0, 1))
        pp = [p["ph"], p["pd"], p["pa"]]
        ll -= math.log(max(pp[y.index(1)], 1e-12))
        rps += 0.5 * ((pp[0] - y[0]) ** 2 + (pp[0] + pp[1] - y[0] - y[1]) ** 2)
        over = int(r["yh"] + r["ya"] > 2.5)
        oull -= math.log(max(p["over25"] if over else 1 - p["over25"], 1e-12))
    n = len(rows)
    return {"n": n, "ll_1x2": ll / n, "rps": rps / n, "oull_2_5": oull / n}


def _clim(train):
    n = len(train); hw = sum(r["yh"] > r["ya"] for r in train) / n; dr = sum(r["yh"] == r["ya"] for r in train) / n
    return [hw, dr, 1 - hw - dr], sum(r["yh"] + r["ya"] > 2.5 for r in train) / n


def run_dev():
    rows = load(SE, set(DEV_SEASONS), forbid=FORBIDDEN_DEV)
    assert {r["season"] for r in rows} <= set(DEV_SEASONS), "dev loader saw a non-dev season"
    result = []
    for arm in ("gate_zero", "shrink", "x2"):
        all_rows = []
        all_clim = []
        for season in SCORED_SEASONS:
            target = [r for r in rows if r["season"] == season]
            assert len(target) == EXPECTED_SCORED_N, f"{season}: expected {EXPECTED_SCORED_N} scored rows, got {len(target)}"
            train = [r for r in rows if r["date"] < min(x["date"] for x in target)]
            model, movers, mult, counts = _fit_predict(train, target, arm)
            probs = [model.probs(*adjusted_lambdas(model, r["hi"], r["ai"], arm, movers, mult, counts)) for r in target]
            met = _scores(target, probs); met.update({"arm": arm, "season": season, "kind": "model"}); result.append(met); all_rows += list(zip(target, probs))
            cp, co = _clim(train)
            cprobs = [{"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target]
            met = _scores(target, cprobs); met.update({"arm": arm, "season": season, "kind": "climatology"}); result.append(met); all_clim += list(zip(target, cprobs))
        assert len(all_rows) == 888, f"pooled scored n expected 888, got {len(all_rows)}"
        met = _scores([x[0] for x in all_rows], [x[1] for x in all_rows]); met.update({"arm": arm, "season": "pooled", "kind": "model"}); result.append(met)
        # Pooled climatology = pooled score of the per-season (expanding,
        # prior-seasons-only) climatology predictions, per the prereg.
        met = _scores([x[0] for x in all_clim], [x[1] for x in all_clim]); met.update({"arm": arm, "season": "pooled", "kind": "climatology"}); result.append(met)
    _write_dev(result)
    _print_table(result, "dev")
    return result


def _write_dev(result):
    (OUT / "results_dev.json").write_text(json.dumps(result, indent=2) + "\n")
    fields = ["arm", "season", "kind", "n", "ll_1x2", "rps", "oull_2_5"]
    with open(OUT / "results_dev.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows({k: r.get(k) for k in fields} for r in result)


def _print_table(data, label):
    print(label)
    if label == "dev":
        print("arm season kind n ll_1x2 rps oull_2_5")
        for r in data: print(f'{r["arm"]} {r["season"]} {r["kind"]} {r["n"]} {r["ll_1x2"]:.6f} {r["rps"]:.6f} {r["oull_2_5"]:.6f}')
