import json
import csv
import os
import glob

OUTPUT = "/mnt/d/projects/prompt-wall/agent-strike/data/missed_samples.csv"
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
            # extract verdict from nested dict
            first = outputs[0]
            verdict = first.get("text", "") if isinstance(first, dict) else str(first)
            if verdict not in ("ALLOW", "BLOCK"):
                continue
            if verdict == "ALLOW":
                try:
                    text = rec["prompt"]["turns"][0]["content"]["text"]
                except:
                    continue
                probe = rec.get("probe_classname", "unknown")
                rows.append({
                    "prompt": text,
                    "expected": "BLOCK",
                    "actual": "ALLOW",
                    "outcome": "FN",
                    "probe": probe,
                    "source_file": os.path.basename(jsonl_file)
                })

with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["prompt","expected","actual","outcome","probe","source_file"])
    writer.writeheader()
    writer.writerows(rows)

print(f"Total genuine FN samples: {len(rows)}")
print(f"Saved to: {OUTPUT}")

from collections import Counter
by_probe = Counter(r["probe"] for r in rows)
for probe, count in by_probe.most_common():
    print(f"  {probe}: {count}")
