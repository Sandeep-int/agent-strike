import csv
import os
from datetime import datetime, timezone

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
RESULTS_FILE = os.path.join(DATA_DIR, "agent_results.csv")
MISSED_FILE = os.path.join(DATA_DIR, "missed_samples.csv")

FIELDNAMES = ["timestamp", "category", "verdict", "layer", "latency_ms", "prompt", "error"]


def _ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _write_row(filepath: str, row: dict):
    file_exists = os.path.isfile(filepath)
    with open(filepath, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def log_result(verdict: dict):
    """
    Logs one attack verdict to agent_results.csv.
    If verdict is ALLOW (FN — attack got through), also logs to missed_samples.csv.
    """
    _ensure_dir()
    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "category": verdict.get("category", "unknown"),
        "verdict": verdict.get("verdict", "UNKNOWN"),
        "layer": verdict.get("layer") or "",
        "latency_ms": verdict.get("latency_ms") or "",
        "prompt": verdict.get("prompt", ""),
        "error": verdict.get("error") or "",
    }
    _write_row(RESULTS_FILE, row)

    if verdict.get("verdict") == "ALLOW":
        _write_row(MISSED_FILE, row)
