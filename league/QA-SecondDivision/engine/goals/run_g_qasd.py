import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dc import run_goals

if __name__ == "__main__":
    result = run_goals(Path(__file__).parent)
    print(json.dumps(result["dev"], indent=1))
    if result["virgin"] is not None:
        print("VIRGIN:", json.dumps(result["virgin"], indent=1))
