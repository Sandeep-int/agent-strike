import os
import json
import time
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# --- Config ---
DEEPSEEK_KEY = os.getenv("AGENT_SHIELD_DATASET_GEN_DEEPSEEK_KEY")
DATA_DIR = Path("/mnt/d/projects/prompt-wall/agent-strike/data")
INPUT_FILE = DATA_DIR / "final_training_dataset.csv"
VERIFIED_FILE = DATA_DIR / "training_data_verified.csv"
DISPUTED_FILE = DATA_DIR / "disputed_rows_pending.csv"
CHECKPOINT_FILE = DATA_DIR / "deepseek_checkpoint.json"
BATCH_SIZE = 500
SLEEP_BETWEEN_BATCHES = 2  # seconds

client = OpenAI(
    api_key=DEEPSEEK_KEY,
    base_url="https://api.deepseek.com"
)

SYSTEM_PROMPT = """You are a prompt injection detection expert.
You will receive a list of text prompts numbered 1 to N.
For each prompt, reply with ONLY a JSON array of objects.
Each object must have:
  "index": the number (1-based)
  "verdict": 1 if it is a prompt injection attack, 0 if it is benign
No explanation. No markdown. Raw JSON array only."""

def load_checkpoint():
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE) as f:
            return json.load(f)
    return {"last_completed_batch": -1}

def save_checkpoint(batch_index):
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump({"last_completed_batch": batch_index}, f)

def build_user_message(rows):
    lines = []
    for i, row in enumerate(rows, 1):
        prompt_text = str(row["prompt"]).replace("\n", " ").strip()
        lines.append(f"{i}. {prompt_text}")
    return "\n".join(lines)

def call_deepseek(rows):
    user_msg = build_user_message(rows)
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg}
        ],
        temperature=0,
        max_tokens=2000
    )
    raw = response.choices[0].message.content.strip()
    return json.loads(raw)

def process():
    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded {len(df)} rows.")

    checkpoint = load_checkpoint()
    start_batch = checkpoint["last_completed_batch"] + 1
    print(f"Resuming from batch {start_batch}.")

    verified_rows = []
    disputed_rows = []

    batches = [df.iloc[i:i+BATCH_SIZE] for i in range(0, len(df), BATCH_SIZE)]
    total = len(batches)

    for batch_idx in range(start_batch, total):
        batch = batches[batch_idx]
        rows = batch.to_dict("records")

        print(f"Batch {batch_idx+1}/{total} — rows {batch.index[0]}–{batch.index[-1]}")

        try:
            verdicts = call_deepseek(rows)
        except Exception as e:
            print(f"ERROR batch {batch_idx}: {e}")
            print("Saving progress and stopping. Re-run to resume.")
            break

        for item in verdicts:
            idx = item["index"] - 1
            if idx >= len(rows):
                continue
            row = rows[idx].copy()
            ds_verdict = int(item["verdict"])
            orig_label = int(row.get("label", -1))

            if ds_verdict == orig_label:
                verified_rows.append(row)
            else:
                row["deepseek_verdict"] = ds_verdict
                disputed_rows.append(row)

        save_checkpoint(batch_idx)
        time.sleep(SLEEP_BETWEEN_BATCHES)

    # Write outputs
    if verified_rows:
        vdf = pd.DataFrame(verified_rows)
        if VERIFIED_FILE.exists():
            vdf.to_csv(VERIFIED_FILE, mode="a", header=False, index=False)
        else:
            vdf.to_csv(VERIFIED_FILE, index=False)

    if disputed_rows:
        ddf = pd.DataFrame(disputed_rows)
        if DISPUTED_FILE.exists():
            ddf.to_csv(DISPUTED_FILE, mode="a", header=False, index=False)
        else:
            ddf.to_csv(DISPUTED_FILE, index=False)

    print(f"Done. Verified: {len(verified_rows)} | Disputed: {len(disputed_rows)}")

if __name__ == "__main__":
    process()
