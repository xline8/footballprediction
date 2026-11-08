import json
from pathlib import Path
from dc import run_goals


if __name__ == "__main__":
    print(json.dumps(run_goals(Path(__file__).parent), indent=1))
