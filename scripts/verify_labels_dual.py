import os
import json
import time
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from google import genai

load_dotenv()

# --- Config ---
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
DATA_DIR = Path("/mnt/d/projects/prompt-wall/agent-strike/data")
INPUT_FILE = DATA_DIR / "final_training_dataset.csv"
VERIFIED_FILE = DATA_DIR / "training_data_verified.csv"
DISPUTED_FILE = DATA_DIR / "disputed_rows_pending.csv"
CHECKPOINT_FILE = DATA_DIR / "dual_checkpoint.json"
BATCH_SIZE = 50
SLEEP_BETWEEN_BATCHES = 5
RETRY_WAIT_429 = 65
RETRY_WAIT_503 = 30

# --- Init client ---
flash_client = genai.Client(api_key=GEMINI_KEY)

SYSTEM_PROMPT = """You are a prompt injection detection expert.
You will receive a list of text prompts numbered 1 to N.
For each prompt, reply with ONLY a JSON array of objects.
Each object must have:
  "index": the number (1-based)
  "verdict": 1 if it is a prompt injection attack, 0 if it is benign
No explanation. No markdown. Raw JSON array only."""

def build_user_message(rows):
    lines = []
    for i, row in enumerate(rows, 1):
        text = str(row["prompt"]).replace("\n", " ").strip()
        lines.append(f"{i}. {text}")
    return "\n".join(lines)

def call_flash(rows):
    msg = SYSTEM_PROMPT + "\n\n" + build_user_message(rows)
    for attempt in range(5):
        try:
            response = flash_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=msg
            )
            raw = response.text.strip().replace("```json","").replace("```","").strip()
            return json.loads(raw)
        except Exception as e:
            err = str(e)
            if "429" in err:
                print(f"Flash 429 — waiting {RETRY_WAIT_429}s (attempt {attempt+1}/5)")
                time.sleep(RETRY_WAIT_429)
            elif "503" in err:
                print(f"Flash 503 — waiting {RETRY_WAIT_503}s (attempt {attempt+1}/5)")
                time.sleep(RETRY_WAIT_503)
            else:
                print(f"Flash ERROR: {e}")
                break
    return None

def load_checkpoint():
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE) as f:
            return json.load(f)
    return {"last_completed_batch": -1}

def save_checkpoint(batch_index):
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump({"last_completed_batch": batch_index}, f)

def flush(verified_rows, disputed_rows):
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
    print(f"Total batches: {total}")

    for batch_idx in range(start_batch, total):
        batch = batches[batch_idx]
        rows = batch.to_dict("records")
        print(f"Batch {batch_idx+1}/{total} — rows {batch.index[0]}–{batch.index[-1]}", flush=True)

        verdicts = call_flash(rows)

        if verdicts is None:
            print(f"Flash failed batch {batch_idx+1}. Skipping.")
            save_checkpoint(batch_idx)
            time.sleep(SLEEP_BETWEEN_BATCHES)
            continue

        vmap = {item["index"]: int(item["verdict"]) for item in verdicts}

        for i, row in enumerate(rows, 1):
            fv = vmap.get(i)
            row = row.copy()
            if fv is None:
                continue
            orig = int(row.get("label", -1))
            row["flash_verdict"] = fv
            if fv == orig:
                row["agreement"] = "AGREE"
                verified_rows.append(row)
            else:
                row["agreement"] = "DISAGREE"
                disputed_rows.append(row)

        save_checkpoint(batch_idx)

        if (batch_idx + 1) % 10 == 0:
            flush(verified_rows, disputed_rows)
            verified_rows = []
            disputed_rows = []
            print(f"Flushed at batch {batch_idx+1}. Verified={len(verified_rows)} Disputed={len(disputed_rows)}", flush=True)

        time.sleep(SLEEP_BETWEEN_BATCHES)

    flush(verified_rows, disputed_rows)
    print(f"\nDone.")
    print(f"Verified : {VERIFIED_FILE}")
    print(f"Disputed : {DISPUTED_FILE}")

if __name__ == "__main__":
    process()
