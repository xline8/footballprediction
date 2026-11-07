"""Train/backtest/predict shots-on-target totals without mutating master data."""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import unicodedata
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

BASE = Path(__file__).resolve().parent
MASTER = BASE / "all_matches_clean.csv"
HALF_LABELS = BASE / "data_enrichment" / "pilot_sot" / "E0_2024-25" / "sot_halves.csv"
ODDS = Path(r"D:\Project\Par\Leeparlay\artifacts\1xbet\all_market_outcomes.csv")
UPCOMING = BASE / "predictions_upcoming.csv"
OUT = BASE / "data_enrichment" / "sot_model"

TARGETS = ("ft", "1h", "2h")
MARKETS = {"ft": "Shots On Target", "1h": "Shots On Target. 1st half",
           "2h": "Shots On Target. 2nd half"}
ALIASES = {"man united": "manchester united", "man city": "manchester city",
           "nottm forest": "nottingham forest", "west ham": "west ham united",
           "wolves": "wolverhampton wanderers"}


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = value.encode("ascii", "ignore").decode().lower()
    value = re.sub(r"[^a-z0-9]+", " ", value).strip()
    return ALIASES.get(value, value)


def num(value: str | None) -> float | None:
    try:
        return float(value) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None


def poisson_tail(mu: float, line: float) -> float:
    p = math.exp(-max(mu, 1e-6))
    total = p
    k = 0
    while k < 80:
        k += 1
        p *= mu / k
        if k > line:
            total += p
        if k > mu + 40 and p < 1e-12:
            break
    return min(max(total, 0.0), 1.0)


def load_rows() -> list[dict]:
    with MASTER.open(encoding="utf-8", newline="") as handle:
        rows = []
        for row in csv.DictReader(handle):
            if row.get("FTR") not in {"H", "D", "A"} or not row.get("Date"):
                continue
            hst, ast = num(row.get("HST")), num(row.get("AST"))
            if hst is None or ast is None:
                continue
            rows.append({
                "div": row["Div"], "season": row["Season"], "date": row["Date"],
                "home": row["HomeTeam"], "away": row["AwayTeam"],
                "ft": int(hst + ast), "ft_home": int(hst), "ft_away": int(ast),
                "1h": None, "2h": None,
            })
    half = {}
    if HALF_LABELS.exists():
        with HALF_LABELS.open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                half[(row["date"], norm(row["home"]), norm(row["away"]))] = (
                    int(row["sot_1h"]), int(row["sot_2h"]))
    for row in rows:
        pair = half.get((row["date"], norm(row["home"]), norm(row["away"])))
        if pair:
            row["1h"], row["2h"] = pair
    return sorted(rows, key=lambda row: (row["date"], row["div"]))


class RollingModel:
    def __init__(self, target: str):
        self.target = target
        self.global_values: deque[float] = deque(maxlen=80)
        self.home_for: dict[str, deque[float]] = defaultdict(lambda: deque(maxlen=8))
        self.away_for: dict[str, deque[float]] = defaultdict(lambda: deque(maxlen=8))
        self.home_against: dict[str, deque[float]] = defaultdict(lambda: deque(maxlen=8))
        self.away_against: dict[str, deque[float]] = defaultdict(lambda: deque(maxlen=8))

    @staticmethod
    def _mean(values: deque[float]) -> float | None:
        return sum(values) / len(values) if values else None

    def predict(self, home: str, away: str) -> float | None:
        if not self.global_values:
            return None
        league_total = self._mean(self.global_values) or 0.1
        league_home = league_total / 2
        league_away = league_total / 2
        home_for = self._mean(self.home_for[norm(home)]) or league_home
        away_for = self._mean(self.away_for[norm(away)]) or league_away
        home_against = self._mean(self.home_against[norm(home)]) or league_away
        away_against = self._mean(self.away_against[norm(away)]) or league_home
        expected_home = (home_for + away_against) / 2
        expected_away = (away_for + home_against) / 2
        return max(0.1, expected_home + expected_away)

    def update(self, row: dict) -> None:
        value = row.get(self.target)
        if value is None:
            return
        home, away = norm(row["home"]), norm(row["away"])
        value = float(value)
        self.global_values.append(value)
        if self.target == "ft":
            home_value = float(row["ft_home"])
            away_value = float(row["ft_away"])
        else:
            home_value = away_value = value / 2
        self.home_for[home].append(home_value)
        self.away_against[away].append(home_value)
        self.away_for[away].append(away_value)
        self.home_against[home].append(away_value)


def backtest(rows: list[dict], target: str) -> tuple[list[dict], dict]:
    model = RollingModel(target)
    predictions = []
    actual_rows = [row for row in rows if row.get(target) is not None]
    for row in actual_rows:
        mu = model.predict(row["home"], row["away"])
        if mu is not None:
            actual = int(row[target])
            predictions.append({**row, "target": target, "actual": actual,
                                "expected": round(mu, 4),
                                "exact": int(round(mu) == actual),
                                "within_one": int(abs(round(mu) - actual) <= 1),
                                "absolute_error": round(abs(mu - actual), 4)})
        model.update(row)
    n = len(predictions)
    lines = sorted({float(row[target]) + 0.5 for row in predictions}) if predictions else []
    line_accuracy = {
        str(line): round(sum(
            (row["actual"] > line) == (row["expected"] > line)
            for row in predictions
        ) / n, 4) if n else None for line in lines}
    metrics = {
        "target": target, "n": n,
        "exact_count_accuracy": round(sum(r["exact"] for r in predictions) / n, 4) if n else None,
        "within_one_accuracy": round(sum(r["within_one"] for r in predictions) / n, 4) if n else None,
        "mae": round(sum(r["absolute_error"] for r in predictions) / n, 4) if n else None,
        "over_under_accuracy_by_line": line_accuracy,
        "label_rows": len(actual_rows), "coverage": round(len(actual_rows) / len(rows), 4) if rows else 0,
    }
    return predictions, metrics


def load_odds() -> dict[tuple[str, str, str], list[dict]]:
    if not ODDS.exists():
        return {}
    with ODDS.open(encoding="utf-8-sig", newline="") as handle:
        grouped = defaultdict(list)
        for row in csv.DictReader(handle):
            market = row.get("context", "")
            target = next((key for key, value in MARKETS.items() if market == value), None)
            if target is None or row.get("blocked", "False").lower() == "true":
                continue
            fixture = row.get("fixture", "")
            if " - " not in fixture or num(row.get("decimal_odds")) is None:
                continue
            home, away = fixture.split(" - ", 1)
            key = (norm(home), norm(away), target)
            grouped[key].append({**row, "target": target,
                                 "odds": float(row["decimal_odds"]),
                                 "line_value": num(row.get("line"))})
    return {key: sorted(value, key=lambda item: item.get("checked_utc", ""))[-1:]
            for key, value in grouped.items()}


def upcoming_predictions(rows: list[dict], odds: dict) -> list[dict]:
    if not UPCOMING.exists():
        return []
    models = {}
    for target in TARGETS:
        models[target] = RollingModel(target)
        for row in rows:
            models[target].update(row)
    with UPCOMING.open(encoding="utf-8", newline="") as handle:
        fixtures = list(csv.DictReader(handle))
    output = []
    for fixture in fixtures:
        result = {key: fixture.get(key, "") for key in ("div", "date", "time", "home", "away")}
        for target in TARGETS:
            mu = models[target].predict(fixture.get("home", ""), fixture.get("away", ""))
            result[f"expected_sot_{target}"] = round(mu, 4) if mu is not None else ""
            market = odds.get((norm(fixture.get("home", "")), norm(fixture.get("away", "")), target), [])
            if market:
                item = market[0]
                result[f"line_{target}"] = item.get("line", "")
                result[f"odds_{target}"] = item.get("odds", "")
                result[f"checked_utc_{target}"] = item.get("checked_utc", "")
                line = item.get("line_value")
                result[f"p_model_over_{target}"] = round(poisson_tail(mu, line), 4) if line is not None else ""
            else:
                result[f"line_{target}"] = result[f"odds_{target}"] = ""
                result[f"checked_utc_{target}"] = result[f"p_model_over_{target}"] = ""
        output.append(result)
    return output


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        fields = list(rows[0]) if rows else []
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backtest", action="store_true")
    parser.add_argument("--predict", action="store_true")
    args = parser.parse_args()
    if not args.backtest and not args.predict:
        args.backtest = args.predict = True
    rows = load_rows()
    OUT.mkdir(parents=True, exist_ok=True)
    report = {"created_at": datetime.now(timezone.utc).isoformat(), "rows": len(rows), "metrics": {}}
    if args.backtest:
        for target in TARGETS:
            predictions, metrics = backtest(rows, target)
            write_csv(OUT / f"backtest_{target}.csv", predictions)
            report["metrics"][target] = metrics
    if args.predict:
        upcoming = upcoming_predictions(rows, load_odds())
        write_csv(BASE / "predictions_sot_upcoming.csv", upcoming)
        report["upcoming_rows"] = len(upcoming)
        report["upcoming_odds_matches"] = {
            target: sum(bool(row.get(f"odds_{target}")) for row in upcoming)
            for target in TARGETS
        }
    (OUT / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
