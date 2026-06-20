from __future__ import annotations

import importlib.util
import subprocess
import sys


def main() -> None:
    if importlib.util.find_spec("duckdb") is None:
        print("duckdb module not installed; run `uv run --with duckdb python projects/duckdb-analytics-lab/app.py`")
        return
    subprocess.run([sys.executable, "projects/duckdb-analytics-lab/app.py"], check=True)


if __name__ == "__main__":
    main()

