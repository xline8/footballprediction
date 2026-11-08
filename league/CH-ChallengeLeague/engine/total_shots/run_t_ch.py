import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from common_nb import run_candidate
if __name__ == "__main__":
    res = run_candidate("T-CH", ("total_shots_home", "total_shots_away"),
                        26.5, [24.5, 26.5, 28.5], ["2023/2024"], ["2024/2025"],
                        "2025/2026", Path(__file__).parent)
    print(res["dev"]); print("VIRGIN:", res["virgin"])
