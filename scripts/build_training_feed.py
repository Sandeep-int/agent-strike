import json
import csv
import os
import glob

OUTPUT = "/mnt/d/projects/prompt-wall/agent-strike/data/garak_training_feed.csv"
RESULTS_DIR = "/mnt/d/projects/prompt-wall/agent-strike/garak/results"

os.makedirs("/mnt/d/projects/prompt-wall/agent-strike/data", exist_ok=True)

rows = []

for jsonl_file in glob.glob(f"{RESULTS_DIR}/*.report.jsonl"):
    with open(jsonl_file) as f:
        for line in f:
            try:
                rec = json.loads(line)
            except:
                continue
            if rec.get("entry_type") != "attempt":
                continue
            outputs = rec.get("outputs", [])
            if not outputs:
                continue
            first = outputs[0]
            verdict = first.get("text", "") if isinstance(first, dict) else str(first)
            if verdict not in ("ALLOW", "BLOCK"):
                continue
            try:
                text = rec["prompt"]["turns"][0]["content"]["text"]
            except:
                continue
            probe = rec.get("probe_classname", "unknown")
            # all attack probes = label 1
            label = 1
            outcome = "FN" if verdict == "ALLOW" else "TP"
            rows.append({
                "prompt": text,
                "label": label,
                "outcome": outcome,
                "verdict": verdict,
                "probe": probe,
                "source_file": os.path.basename(jsonl_file)
            })

with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["prompt","label","outcome","verdict","probe","source_file"])
    writer.writeheader()
    writer.writerows(rows)

from collections import Counter
outcomes = Counter(r["outcome"] for r in rows)
print(f"Total rows: {len(rows)}")
print(f"TP (correctly blocked): {outcomes['TP']}")
print(f"FN (missed attacks):    {outcomes['FN']}")
print(f"Saved to: {OUTPUT}")
