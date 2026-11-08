import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from dc import run_goals
if __name__ == "__main__":
    res = run_goals(Path(__file__).parent)
    import json
    print(json.dumps(res["dev"], indent=1))
    print("VIRGIN:", json.dumps(res["virgin"], indent=1) if res["virgin"] else None)
