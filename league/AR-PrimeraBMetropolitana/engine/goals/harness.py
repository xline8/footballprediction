"""DEV-only expanding block-blocked walk-forward harness for G-PBM."""
import csv, json, math
from collections import defaultdict, deque
from datetime import date
from itertools import islice
from pathlib import Path

from arms import adjusted_lambdas, newcomer_ids, GF_GAP, GA_GAP
from dc import DC

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "pbm_matches.csv"
OUT = Path(__file__).resolve().parent
DEV_BLOCKS = ("2021", "2022", "2023", "2024", "2025")
SCORED_BLOCKS = ("2022", "2023", "2024", "2025")
EXPECTED_DEV_N = 1698
EXPECTED_SCORED_N = 1426


def load_dev_rows():
    """Load only the known 2021-2025 prefix; never consume a 2026 row."""
    rows = []
    with DATA.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in islice(reader, EXPECTED_DEV_N):
            assert r["season"] != "2026", "DEV loader touched a 2026 row"
            assert r["season"] in DEV_BLOCKS, f"unexpected dev block {r['season']}"
            rows.append({"match_id": r["match_id"], "season": r["season"],
                         "date": date.fromisoformat(r["date"]),
                         "hi": int(r["home_team_id"]), "ai": int(r["away_team_id"]),
                         "home": r["home_team"], "away": r["away_team"],
                         "yh": int(r["home_goals"]), "ya": int(r["away_goals"])})
    assert len(rows) == EXPECTED_DEV_N
    assert all(r["season"] != "2026" for r in rows)
    return sorted(rows, key=lambda r: (r["date"], r["match_id"]))


def scores(rows, probs):
    ll = rps = oull = 0.0
    for r, p in zip(rows, probs):
        y = (1, 0, 0) if r["yh"] > r["ya"] else ((0, 1, 0) if r["yh"] == r["ya"] else (0, 0, 1))
        q = (p["ph"], p["pd"], p["pa"])
        ll -= math.log(max(q[y.index(1)], 1e-12))
        rps += 0.5 * ((q[0] - y[0]) ** 2 + (q[0] + q[1] - y[0] - y[1]) ** 2)
        over = int(r["yh"] + r["ya"] > 2.5)
        oull -= math.log(max(p["over25"] if over else 1 - p["over25"], 1e-12))
    n = len(rows)
    return {"n": n, "ll_1x2": ll / n, "rps": rps / n, "oull_2_5": oull / n}


def climatology_probs(train):
    n = len(train)
    ph = sum(r["yh"] > r["ya"] for r in train) / n
    pd = sum(r["yh"] == r["ya"] for r in train) / n
    return {"ph": ph, "pd": pd, "pa": 1 - ph - pd,
            "over25": sum(r["yh"] + r["ya"] > 2.5 for r in train) / n}


def trailing10_probs(train, target):
    league_goals = sum(r["yh"] + r["ya"] for r in train) / (2 * len(train))
    history = defaultdict(list)
    for r in sorted(train, key=lambda x: (x["date"], x["match_id"])):
        history[r["hi"]].append((r["date"], r["yh"], r["ya"]))
        history[r["ai"]].append((r["date"], r["ya"], r["yh"]))
    out = []
    for r in target:
        h = history[r["hi"]][-10:]
        a = history[r["ai"]][-10:]
        hgf = sum(x[1] for x in h) / len(h) if h else league_goals
        hga = sum(x[2] for x in h) / len(h) if h else league_goals
        agf = sum(x[1] for x in a) / len(a) if a else league_goals
        aga = sum(x[2] for x in a) / len(a) if a else league_goals
        out.append(((hgf + aga) / 2, (agf + hga) / 2))
    return out


def block_table(rows, arm):
    results = []
    pools = {"model": [], "climatology": [], "trailing10": []}
    newcomers_by_block = {}
    example = None
    for block in SCORED_BLOCKS:
        target = [r for r in rows if r["season"] == block]
        cutoff = min(r["date"] for r in target)
        train = [r for r in rows if r["date"] < cutoff]
        model = DC().fit(train, cutoff)
        newcomers = newcomer_ids(block, rows)
        newcomers_by_block[block] = sorted(newcomers)
        model_probs = []
        for r in target:
            lh, la, offsets = adjusted_lambdas(model, r["hi"], r["ai"], arm, newcomers)
            p = model.probs(lh, la); p.update(lh=lh, la=la)
            model_probs.append(p)
            if example is None and arm == "x2" and offsets:
                team = sorted(offsets)[0]
                example = {"team": team, "team_name": model.team_names.get(team, r["home"] if team == r["hi"] else r["away"]),
                           "block": block, "mu": model.mu, "attack_offset": offsets[team]["attack"],
                           "defence_offset": offsets[team]["defence"]}
        cp = climatology_probs(train)
        clim_probs = [cp] * len(target)
        trail_lams = trailing10_probs(train, target)
        trail_probs = [model.probs(lh, la) for lh, la in trail_lams]
        for kind, ps in (("model", model_probs), ("climatology", clim_probs), ("trailing10", trail_probs)):
            met = scores(target, ps)
            met.update({"arm": arm, "block": block, "kind": kind})
            results.append(met)
            pools[kind].extend(zip(target, ps))
    for kind, pairs in pools.items():
        met = scores([x[0] for x in pairs], [x[1] for x in pairs])
        met.update({"arm": arm, "block": "pooled", "kind": kind})
        results.append(met)
    return results, newcomers_by_block, example


def gate_arithmetic(table, arm):
    pooled = {(r["kind"]): r for r in table if r["block"] == "pooled"}
    model, clim, trail = pooled["model"], pooled["climatology"], pooled["trailing10"]
    legs = {
        "ll_1x2_vs_climatology": {"value": model["ll_1x2"] - clim["ll_1x2"], "pass": model["ll_1x2"] < clim["ll_1x2"]},
        "rps_vs_climatology": {"value": model["rps"] - clim["rps"], "pass": model["rps"] < clim["rps"]},
        "oull_2_5_vs_base_rate": {"value": model["oull_2_5"] - clim["oull_2_5"], "pass": model["oull_2_5"] < clim["oull_2_5"]},
        "trailing10_reference_ll_1x2_margin": {"value": model["ll_1x2"] - trail["ll_1x2"]},
        "trailing10_reference_rps_margin": {"value": model["rps"] - trail["rps"]},
        "trailing10_reference_oull_2_5_margin": {"value": model["oull_2_5"] - trail["oull_2_5"]},
    }
    # Leg (iii) is the per-block sign record against Gate Zero and is computed below.
    passed = all(x["pass"] for x in legs.values() if "pass" in x)
    return {"arm": arm, "legs": legs, "dev_gate_pass": passed}


def run_dev():
    rows = load_dev_rows()
    assert len([r for r in rows if r["season"] in SCORED_BLOCKS]) == EXPECTED_SCORED_N
    all_tables = []
    details = {}
    for arm in ("gate_zero", "x2"):
        table, newcomers, example = block_table(rows, arm)
        all_tables.extend(table)
        details[arm] = {"newcomers_by_block": newcomers, "newcomer_example": example}
    for arm in ("gate_zero", "x2"):
        g = gate_arithmetic([r for r in all_tables if r["arm"] == arm], arm)
        details[arm]["dev_gate"] = g
    gz = {r["block"]: r for r in all_tables if r["arm"] == "gate_zero" and r["kind"] == "model"}
    for arm in ("gate_zero", "x2"):
        sign = []
        for block in SCORED_BLOCKS:
            x = next(r for r in all_tables if r["arm"] == arm and r["kind"] == "model" and r["block"] == block)
            sign.append({"block": block, "ll_margin_vs_gate_zero": x["ll_1x2"] - gz[block]["ll_1x2"],
                         "pass": x["ll_1x2"] <= gz[block]["ll_1x2"]})
        details[arm]["dev_block_sign_record_vs_gate_zero"] = sign
        if arm == "x2":
            details[arm]["dev_gate"]["legs"]["per_block_sign_check"] = {"value": sum(x["pass"] for x in sign), "required": 2, "pass": sum(x["pass"] for x in sign) >= 2}
            details[arm]["dev_gate"]["dev_gate_pass"] = details[arm]["dev_gate"]["dev_gate_pass"] and details[arm]["dev_gate"]["legs"]["per_block_sign_check"]["pass"]
    output = {"scope": {"mode": "dev", "blocks": list(SCORED_BLOCKS), "warmup": "2021", "n_dev": len(rows), "n_scored": EXPECTED_SCORED_N, "read_2026": False},
              "constants": {"half_life": 270, "rho_grid": list((0.0, -0.05, -0.10, -0.15)), "sweeps": 14, "damping": 0.7, "smoothing": 0.25, "home_adv_init": 0.28, "maxg": 10, "gf_gap": GF_GAP, "ga_gap": GA_GAP},
              "tables": all_tables, "arms": details}
    (OUT / "results_dev.json").write_text(json.dumps(output, indent=2, sort_keys=False) + "\n")
    fields = ["arm", "block", "kind", "n", "ll_1x2", "rps", "oull_2_5"]
    with (OUT / "results_dev.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader()
        writer.writerows({k: row.get(k, "") for k in fields} for row in all_tables)
    print(json.dumps(output, indent=2))
    return output
