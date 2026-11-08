import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from common_nb import run_candidate
if __name__ == "__main__":
    res = run_candidate("K-CH", ("yellow_cards_home", "yellow_cards_away"),
                        4.5, [3.5, 4.5, 5.5], ["2023/2024"], ["2024/2025"],
                        "2025/2026", Path(__file__).parent)
    print(res["dev"]); print("VIRGIN:", res["virgin"])
