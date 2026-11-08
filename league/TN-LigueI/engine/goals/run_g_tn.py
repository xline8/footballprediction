import json
from pathlib import Path
from dc import run_goals


if __name__ == "__main__":
    result = run_goals(Path(__file__).parent)
    print(json.dumps(result["dev"], indent=1))
