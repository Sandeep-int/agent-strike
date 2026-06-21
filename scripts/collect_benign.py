import os, csv, time, requests, json
from dotenv import load_dotenv

load_dotenv()

API_URL    = "https://agent-shield-chbxh2hkhxgucgax.eastasia-01.azurewebsites.net/v1/check"
API_KEY    = os.getenv("AGENT_STRIKE_INTERNAL_KEY")
OUTPUT     = "/mnt/d/projects/prompt-wall/agent-strike/data/benign_verdicts.csv"
CHECKPOINT = "/mnt/d/projects/prompt-wall/agent-strike/data/benign_progress.txt"
TARGET     = 23412
HEADERS    = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

def get_progress():
    if os.path.exists(CHECKPOINT):
        return int(open(CHECKPOINT).read().strip())
    return 0

def save_progress(n):
    open(CHECKPOINT, "w").write(str(n))

def fire(prompt):
    try:
        r = requests.post(API_URL, json={"prompt": prompt[:2000]}, headers=HEADERS, timeout=30)
        if r.status_code == 200:
            d = r.json()
            return d.get("verdict"), d.get("confidence", 0.0), d.get("layer_hit", "")
        return None, 0.0, "HTTP_ERROR"
    except Exception:
        return None, 0.0, "EXCEPTION"

print("Downloading alpaca from HF...")
url = "https://huggingface.co/datasets/tatsu-lab/alpaca/resolve/main/data/train-00000-of-00001-a09b74b3ef9c3b56.parquet"
r = requests.get(url, timeout=60)
open("/tmp/alpaca.parquet", "wb").write(r.content)
print("Download done")

import struct, io

# Use pandas to read parquet — lighter than datasets library
import subprocess
subprocess.run(["pip", "install", "pandas", "pyarrow", "-q"])
import pandas as pd
df = pd.read_parquet("/tmp/alpaca.parquet")
prompts = df["instruction"].dropna().tolist()
prompts = [p.strip() for p in prompts if p.strip()][:TARGET]
print(f"Loaded {len(prompts)} prompts")

start = get_progress()
print(f"Resuming from row {start}")

file_exists = os.path.exists(OUTPUT) and start > 0
with open(OUTPUT, "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    if not file_exists:
        writer.writerow(["prompt", "expected", "actual", "outcome", "layer", "confidence"])

    for i in range(start, len(prompts)):
        prompt = prompts[i]
        verdict, confidence, layer = fire(prompt)

        if verdict is None:
            time.sleep(2)
            continue

        expected = "ALLOW"
        actual   = verdict
        outcome  = "TN" if verdict == "ALLOW" else "FP"

        writer.writerow([prompt[:200], expected, actual, outcome, layer, confidence])
        f.flush()

        if (i + 1) % 100 == 0:
            save_progress(i + 1)
            print(f"Progress: {i+1}/{len(prompts)} | Last: {outcome} | Layer: {layer}")

        time.sleep(0.3)

save_progress(len(prompts))
print("DONE")
