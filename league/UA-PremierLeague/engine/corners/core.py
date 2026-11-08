"""Frozen CN chronological corner model (stdlib only)."""
import csv
import math
from collections import defaultdict
from datetime import date


HALF_LIFE = 270.0
GRID = 50
R_MIN = 1.02
MULT_LO, MULT_HI = 0.70, 1.43
GAMMAS = (0.0, 0.15, 0.3, 0.45, 0.6, 0.8)
BP = (-0.010, -0.0075, -0.005, -0.0025, 0.0, 0.0025, 0.005, 0.0075, 0.010)
BBT = (-0.04, -0.03, -0.02, -0.01, 0.0, 0.01, 0.02, 0.03, 0.04)


def num(value):
    return None if value in (None, "") else float(value)


def load(path, seasons):
    out = []
    with open(path, newline="", encoding="utf-8") as fh:
        for raw in csv.DictReader(fh):
            if raw["season"] not in seasons:
                continue
            if raw["corners_home"] == "" or raw["corners_away"] == "":
                continue  # target absent (score-only match) — never imputed; excluded from this market
            if float(raw["total_shots_home"] or 0) == 0 and float(raw["total_shots_away"] or 0) == 0 and float(raw["ShotsOnTarget_home"] or 0) == 0 and float(raw["ShotsOnTarget_away"] or 0) == 0 and float(raw["corners_home"]) == 0 and float(raw["corners_away"]) == 0:
                continue  # UA stub row: stats-missing (PREPROCESSING rule 2)
            out.append({
                "match_id": raw["match_id"], "season": raw["season"],
                "date": date.fromisoformat(raw["date"]),
                "home_id": raw["home_team_id"], "away_id": raw["away_team_id"],
                "home": raw["home_team"], "away": raw["away_team"],
                "ch": int(float(raw["corners_home"])), "ca": int(float(raw["corners_away"])),
                "sh": num(raw["total_shots_home"]), "sa": num(raw["total_shots_away"]),
                "poss_h": num(raw["BallPossesion_home"]), "poss_a": num(raw["BallPossesion_away"]),
                "bc_h": num(raw["big_chance_home"]), "bc_a": num(raw["big_chance_away"]),
                "bt_h": num(raw["touches_opp_box_home"]), "bt_a": num(raw["touches_opp_box_away"]),
            })
    return sorted(out, key=lambda r: (r["date"], r["match_id"]))


def weight(cutoff, when):
    return 0.5 ** ((cutoff - when).days / HALF_LIFE)


def stats_window(rows, cutoff):
    wh = wa = ws = denom = y2 = ysum = 0.0
    for r in rows:
        if r["date"] >= cutoff:
            continue
        w = weight(cutoff, r["date"])
        wh += w * r["ch"]
        wa += w * r["ca"]
        ws += w * (r["sh"] + r["sa"])
        denom += 2.0 * w
        ysum += w * (r["ch"] + r["ca"])
        y2 += w * (r["ch"] + r["ca"]) ** 2
    if denom == 0.0:
        return 0.0, 0.0, 0.0, 1.02, 0.0
    return wh * 2 / denom, wa * 2 / denom, (wh + wa) * 2 / denom, y2 / max(ysum, 1e-12), ws / denom


def rel_factors(home, away, shot_history, league_shots):
    if league_shots <= 0:
        return (1.0, 1.0, 1.0, 1.0)

    def factor(team, pos):
        vals = shot_history.get(team, [])[-5:]
        if not vals:
            return 1.0
        return max(0.6, min(1.7, sum(v[pos] for v in vals) / len(vals) / league_shots))
    return factor(home, 0), factor(home, 1), factor(away, 0), factor(away, 1)


def territorial(team, key, date_cutoff, history):
    # Entries are all prior matches; only entries with both sides' feature
    # present are valid, and the min-8 rule applies within the last 10 entries.
    entries = history.get(team, [])[-10:]
    valid = [x for x in entries if x[key + "_f"] is not None and x[key + "_a"] is not None]
    if len(valid) < 8:
        return None
    return sum(x[key + "_f"] - x[key + "_a"] for x in valid) / len(valid)


class FeatureBuilder:
    def __init__(self, rows):
        self.rows = rows

    def build(self):
        prior = []
        shot_history = defaultdict(list)
        terr_history = defaultdict(list)
        result = []
        i = 0
        while i < len(self.rows):
            d = self.rows[i]["date"]
            j = i
            while j < len(self.rows) and self.rows[j]["date"] == d:
                j += 1
            bh, ba, base_mu, r_base, league_shots = stats_window(prior, d)
            for row in self.rows[i:j]:
                fhp, fhc, fap, fac = rel_factors(row["home_id"], row["away_id"], shot_history, league_shots)
                ph = territorial(row["home_id"], "poss", d, terr_history)
                pa = territorial(row["away_id"], "poss", d, terr_history)
                # Coordinator correction (CN build, 2026-11-10): z_bc must be
                # the TRAILING territorial big-chance differential (J1
                # original). The TH copy this file was taken from had
                # silently replaced it with the target match's OWN
                # big_chance split — same-match leakage. Restored to J1 form.
                bch = territorial(row["home_id"], "bc", d, terr_history)
                bca = territorial(row["away_id"], "bc", d, terr_history)
                bth = territorial(row["home_id"], "bt", d, terr_history)
                bta = territorial(row["away_id"], "bt", d, terr_history)
                result.append({**row, "y": row["ch"] + row["ca"], "bh": bh, "ba": ba,
                               "base_mu": base_mu, "r_base": r_base, "league_shots": league_shots,
                               "fhp": fhp, "fhc": fhc, "fap": fap, "fac": fac,
                               "z_poss": None if ph is None or pa is None else ph - pa,
                               "z_bc": None if bch is None or bca is None else bch - bca,
                               "z_bt": None if bth is None or bta is None else bth - bta,
                               "both_poss_active": ph is not None and pa is not None,
                               "both_bc_active": bch is not None and bca is not None,
                               "both_bt_active": bth is not None and bta is not None,
                               "prior_n": len(prior)})
            # Feed a whole date only after all predictions for that date exist.
            for row in self.rows[i:j]:
                prior.append(row)
                if row["sh"] is not None and row["sa"] is not None:
                    shot_history[row["home_id"]].append((row["sh"], row["sa"]))
                    shot_history[row["away_id"]].append((row["sa"], row["sh"]))
                for team, f, a in ((row["home_id"], row["poss_h"], row["poss_a"]),
                                   (row["away_id"], row["poss_a"], row["poss_h"])):
                    terr_history[team].append({"poss_f": f, "poss_a": a,
                                               "bc_f": row["bc_h"] if team == row["home_id"] else row["bc_a"],
                                               "bc_a": row["bc_a"] if team == row["home_id"] else row["bc_h"],
                                               "bt_f": row["bt_h"] if team == row["home_id"] else row["bt_a"],
                                               "bt_a": row["bt_a"] if team == row["home_id"] else row["bt_h"]})
            i = j
        return result


def mu_cs(row, gamma):
    return row["bh"] * (row["fhp"] * row["fac"]) ** gamma + row["ba"] * (row["fap"] * row["fhc"]) ** gamma


def multiplier(row, arm, beta):
    if arm == "gate_zero":
        if row["z_poss"] is None:
            return 1.0
        # UA: big_chance absent in every payload -> z_bc is always None;
        # the bc term is inactive by missing data (prereg), poss only.
        raw = math.exp(beta[0] * row["z_poss"] + (beta[1] * row["z_bc"] if row["z_bc"] is not None else 0.0))
    else:
        if row["z_bt"] is None:
            return 1.0
        raw = math.exp(beta[0] * row["z_bt"])
    return max(MULT_LO, min(MULT_HI, raw))


def k_of(r, mu):
    return mu / (r - 1.0) if r > R_MIN else 1e9


def pmf(mu, r):
    if mu <= 0:
        return [1.0] + [0.0] * GRID
    k = k_of(r, mu)
    vals = []
    for y in range(GRID + 1):
        vals.append(math.exp(math.lgamma(y + k) - math.lgamma(k) - math.lgamma(y + 1)
                             + k * math.log(k / (k + mu)) + y * math.log(mu / (k + mu))))
    total = sum(vals)
    return [v / total for v in vals]


def over_prob(mu, r, line):
    p = pmf(mu, r)
    return sum(p[int(line) + 1:])


def binary_ll(p, y):
    p = max(1e-12, min(1.0 - 1e-12, p))
    return -(y * math.log(p) + (1 - y) * math.log(1 - p))


def fit_params(rows, arm):
    train = [x for x in rows if x["prior_n"] >= 10]
    best_gamma = None
    for gamma in GAMMAS:
        mus = [mu_cs(x, gamma) for x in train]
        r = max(1.02, min(5.0, sum((x["y"] - m) ** 2 for x, m in zip(train, mus)) / max(sum(mus), 1e-12)))
        nll = sum(-math.log(max(pmf(m, r)[x["y"]], 1e-12)) for x, m in zip(train, mus)) / len(train)
        candidate = (nll, gamma, r)
        if best_gamma is None or candidate < best_gamma:
            best_gamma = candidate
    _, gamma, r = best_gamma
    grid = [(bp, bbc) for bp in BP for bbc in (-0.10, -0.075, -0.05, -0.025, 0.0, 0.025, 0.05, 0.075, 0.10)] if arm == "gate_zero" else [(b,) for b in BBT]
    scored = []
    for beta in grid:
        loss = 0.0
        for x in train:
            mu = mu_cs(x, gamma) * multiplier(x, arm, beta)
            loss += binary_ll(over_prob(mu, r, 9.5), int(x["y"] > 9.5))
        scored.append((loss / len(train), sum(abs(v) for v in beta), beta))
    _, _, beta = min(scored, key=lambda x: (x[0], x[1], x[2]))
    return {"gamma": gamma, "r": r, "beta": list(beta), "fit_n": len(train)}


def model_prediction(row, params, arm):
    mu = mu_cs(row, params["gamma"]) * multiplier(row, arm, params["beta"])
    return mu, params["r"]


def baseline_prediction(row, baseline):
    if baseline == "league_base_rate":
        return row["season_base_mu"], row["season_r_base"]
    home = row.get("naive_home")
    away = row.get("naive_away")
    return (home + away) / 2.0, row["season_r_base"]


def attach_naive(rows):
    hist = defaultdict(list)
    out = []
    # Coordinator correction (verification, 2026-11-09): naive windows are
    # date-grouped like every other state in this engine — the prereg
    # requires strictly pre-date state, so same-date matches must not see
    # each other in the trailing-10 history either.
    i = 0
    while i < len(rows):
        j = i
        while j < len(rows) and rows[j]["date"] == rows[i]["date"]:
            j += 1
        for row in rows[i:j]:
            h = hist[row["home_id"]][-10:]
            a = hist[row["away_id"]][-10:]
            fallback = (row["bh"] + row["ba"]) / 2.0
            def means(vals):
                if len(vals) < 6:
                    return fallback, fallback
                return sum(v[0] for v in vals) / len(vals), sum(v[1] for v in vals) / len(vals)
            hcf, hca = means(h); acf, aca = means(a)
            out.append({**row, "naive_home": hcf + aca, "naive_away": acf + hca})
        for row in rows[i:j]:
            hist[row["home_id"]].append((row["ch"], row["ca"]))
            hist[row["away_id"]].append((row["ca"], row["ch"]))
        i = j
    by_season = defaultdict(list)
    for row in rows:
        by_season[row["season"]].append(row)
    for season, season_rows in by_season.items():
        cutoff = min(x["date"] for x in season_rows)
        _, _, mu, rb, _ = stats_window(rows, cutoff)
        for row in out:
            if row["season"] == season:
                row["season_base_mu"] = mu
                row["season_r_base"] = rb
    return out
