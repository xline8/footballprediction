#!/usr/bin/env python3
"""Interactive terminal for Football Prediction.

It is a safe entry point for new users and also supports command flags for
cron, VPS, and advanced use.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Sequence


BASE_DIR = Path(__file__).resolve().parent
COMBINED_DATA = BASE_DIR / "all_matches.csv"
TRAINING_DATA = BASE_DIR / "all_matches_clean.csv"
PREDICTIONS = BASE_DIR / "predictions_upcoming.csv"
OUTPUT_FILES = (
    ("Match predictions", "predictions_upcoming.csv"),
    ("Best picks", "best_picks.csv"),
    ("Single recommendation", "recommended_single.csv"),
    ("Slip recommendation", "recommended_slip.csv"),
    ("Slip 10 recommendation", "recommended_slip10.csv"),
)

ABOUT_AND_CREDITS = """\
ABOUT & CREDITS

Football Prediction is a research project for modelling pre-match football
probabilities. It does not guarantee returns and is not betting advice.

Created by: Arif Wicaksono Komarudin (@xline8)
Repository: https://github.com/xline8/footballprediction

Data sources:
  - football-data.co.uk: historical league results, odds, and corner data.
  - Understat: expected-goals (xG) data by season.
  - TipsterArea: fixtures, results, and market-odds snapshots.

Each source has its own terms of use. Check the original source when you need
details about its data or usage terms.
"""


class Style:
    """Optional terminal colours; output remains readable without them."""

    enabled = sys.stdout.isatty() and not os.environ.get("NO_COLOR")

    @classmethod
    def apply(cls, text: str, code: str) -> str:
        return f"\033[{code}m{text}\033[0m" if cls.enabled else text

    @classmethod
    def title(cls, text: str) -> str:
        return cls.apply(text, "1;36")

    @classmethod
    def success(cls, text: str) -> str:
        return cls.apply(text, "1;32")

    @classmethod
    def warning(cls, text: str) -> str:
        return cls.apply(text, "1;33")

    @classmethod
    def error(cls, text: str) -> str:
        return cls.apply(text, "1;31")


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def csv_row_count(path: Path) -> int | None:
    """Return the number of CSV data rows, or None if the file cannot be read."""
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            return sum(1 for _ in csv.DictReader(handle))
    except (OSError, UnicodeError, csv.Error):
        return None


def output_summary() -> list[str]:
    rows: list[str] = []
    for label, filename in OUTPUT_FILES:
        path = BASE_DIR / filename
        if not path.exists():
            rows.append(f"  - {label}: not created yet")
            continue
        count = csv_row_count(path)
        updated = path.stat().st_mtime
        timestamp = datetime.fromtimestamp(updated).strftime("%Y-%m-%d %H:%M")
        detail = "cannot be read" if count is None else f"{count} rows"
        rows.append(f"  - {label}: {detail} (updated {timestamp})")
    return rows


def has_training_data() -> bool:
    """Return whether the cleaned training file contains at least one match."""
    try:
        with TRAINING_DATA.open(encoding="utf-8", newline="") as handle:
            return next(csv.DictReader(handle), None) is not None
    except (OSError, UnicodeError, csv.Error):
        return False


def show_status() -> None:
    print(Style.title("\nPROJECT STATUS"))
    print(f"Project folder: {BASE_DIR}")
    print(f"Python: {sys.version.split()[0]}")
    print("\nOutput files:")
    print("\n".join(output_summary()))

    latest_run = BASE_DIR / "last_full_pipeline.json"
    if latest_run.exists():
        try:
            with latest_run.open(encoding="utf-8") as handle:
                payload = json.load(handle)
            status = payload.get("status", "unknown")
            print(f"\nLast pipeline: {status}")
        except (OSError, ValueError, AttributeError):
            print("\nLast pipeline: status cannot be read")
    else:
        print("\nNo pipeline record yet. Choose menu item 1 to start.")


def show_about_and_credits() -> None:
    print(Style.title("\n" + ABOUT_AND_CREDITS))


def run_command(label: str, arguments: Sequence[str]) -> bool:
    print(Style.title(f"\n-> {label}"))
    print(f"  Running: {sys.executable} {' '.join(arguments)}\n")
    try:
        completed = subprocess.run([sys.executable, *arguments], cwd=BASE_DIR, check=False)
    except OSError as exc:
        print(Style.error(f"Could not start the process: {exc}"))
        return False

    if completed.returncode == 0:
        print(Style.success(f"\n[OK] {label} finished."))
        return True
    print(Style.error(f"\n[ERROR] {label} stopped (exit code {completed.returncode})."))
    return False


def ensure_training_data() -> bool:
    """Create the training dataset when the project is run for the first time."""
    if has_training_data():
        return True

    if not COMBINED_DATA.exists():
        print(Style.warning(
            "\nInitial training data is missing. Downloading match history before "
            "the first run."
        ))
        if not run_command("Downloading historical match data", ("download.py",)):
            return False
    else:
        print(Style.warning(
            "\nThe combined match dataset exists, but the cleaned dataset is missing."
        ))
    if not run_command("Building the combined match dataset", ("prepare.py",)):
        return False
    if not run_command("Cleaning the match dataset", ("clean.py",)):
        return False
    if has_training_data():
        return True

    print(Style.error(
        "[ERROR] The initial data setup did not create a usable "
        "all_matches_clean.csv. Check the network connection and try again."
    ))
    return False


def run_daily_update() -> bool:
    if not ensure_training_data():
        return False
    return run_command("Daily update", ("run_daily_shadow.py",))


def run_local_api() -> bool:
    if not has_training_data():
        print(Style.warning(
            "Training data is missing. Run menu item 1 before starting the API."
        ))
        return False
    if not PREDICTIONS.exists():
        print(Style.warning(
            "Predictions are missing. Run menu item 1 before starting the API."
        ))
        return False
    return run_command("Local API", ("api_server.py",))


def run_full_pipeline() -> bool:
    """Build the cache, then run the complete production pipeline."""
    if not ensure_training_data():
        return False
    if not run_command("Preparing the data cache", ("setup_cache.py",)):
        return False
    return run_command("Updating data and generating predictions", (
        "pipeline_orchestrator.py", "--run-all"
    ))


def confirm(message: str) -> bool:
    try:
        answer = input(f"{message} [y/N]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    return answer in {"y", "yes"}


def open_results() -> None:
    available = [(label, BASE_DIR / filename) for label, filename in OUTPUT_FILES
                 if (BASE_DIR / filename).exists()]
    if not available:
        print(Style.warning("There are no output files yet. Run menu item 1 first."))
        return

    print(Style.title("\nOPEN AN OUTPUT FILE"))
    for index, (label, path) in enumerate(available, start=1):
        print(f"  {index}. {label} - {path.name}")
    print("  0. Back")
    try:
        selected = input("Choose a file: ").strip()
        index = int(selected)
    except (ValueError, EOFError, KeyboardInterrupt):
        print(Style.warning("That choice is not valid."))
        return
    if index == 0:
        return
    if not 1 <= index <= len(available):
        print(Style.warning("That number is not available."))
        return

    path = available[index - 1][1]
    try:
        if os.name == "nt":
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.run(["open", str(path)], check=False)
        else:
            subprocess.run(["xdg-open", str(path)], check=False)
        print(Style.success(f"Opening {path.name}."))
    except OSError as exc:
        print(Style.error(f"Could not open the file: {exc}"))


def wait_for_enter() -> None:
    try:
        input("\nPress Enter to return to the menu...")
    except (EOFError, KeyboardInterrupt):
        print()


def interactive_menu() -> int:
    while True:
        clear_screen()
        print(Style.title("=" * 56))
        print(Style.title("       FOOTBALL PREDICTION - CONTROL CENTER"))
        print(Style.title("=" * 56))
        print("Choose what you want to do:\n")
        print("  1. Update data and generate all predictions")
        print("  2. Run the daily update (live shadow)")
        print("  3. View project status and output files")
        print("  4. Open an output file in a spreadsheet app")
        print("  5. Start the local API (http://127.0.0.1:8000)")
        print("  6. About this project, its creator, and data sources")
        print("  0. Exit")

        try:
            choice = input("\nEnter a menu number: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            return 0

        if choice == "0":
            print("Goodbye.")
            return 0
        if choice == "1":
            if confirm("This uses the internet and can take several minutes. Continue?"):
                run_full_pipeline()
            wait_for_enter()
        elif choice == "2":
            if confirm("Run the daily update now?"):
                run_daily_update()
            wait_for_enter()
        elif choice == "3":
            show_status()
            wait_for_enter()
        elif choice == "4":
            open_results()
            wait_for_enter()
        elif choice == "5":
            print("Press Ctrl+C to stop the API and return to the menu.")
            run_local_api()
            wait_for_enter()
        elif choice == "6":
            show_about_and_credits()
            wait_for_enter()
        else:
            print(Style.warning("Choose a number shown in the menu."))
            wait_for_enter()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Football Prediction Control Center; no arguments opens the interactive menu."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--run-all", action="store_true", help="build the cache and run the complete pipeline")
    group.add_argument("--daily", action="store_true", help="run the daily update")
    group.add_argument("--status", action="store_true", help="show status without opening the menu")
    group.add_argument("--api", action="store_true", help="start the local API")
    group.add_argument("--about", action="store_true", help="show project credits and data sources")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.run_all:
        return 0 if run_full_pipeline() else 1
    if args.daily:
        return 0 if run_daily_update() else 1
    if args.status:
        show_status()
        return 0
    if args.api:
        return 0 if run_local_api() else 1
    if args.about:
        show_about_and_credits()
        return 0
    return interactive_menu()


if __name__ == "__main__":
    raise SystemExit(main())
