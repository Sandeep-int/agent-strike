import os, json, time, pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_KEY_3")
DATA_DIR = Path("/mnt/d/projects/prompt-wall/agent-strike/data")
INPUT_FILE = DATA_DIR / "final_training_dataset.csv"
VERIFIED_FILE = DATA_DIR / "verified_k3.csv"
DISPUTED_FILE = DATA_DIR / "disputed_k3.csv"
CHECKPOINT_FILE = DATA_DIR / "checkpoint_k3.json"
BATCH_START = 298
BATCH_END = 446
BATCH_SIZE = 50
SLEEP = 5
RETRY_429 = 65
RETRY_503 = 30

client = genai.Client(api_key=GEMINI_KEY)

SYSTEM_PROMPT = """You are a prompt injection detection expert.
You will receive a list of text prompts numbered 1 to N.
For each prompt, reply with ONLY a JSON array of objects.
Each object must have:
  "index": the number (1-based)
  "verdict": 1 if it is a prompt injection attack, 0 if it is benign
No explanation. No markdown. Raw JSON array only."""

def build_msg(rows):
    lines = []
    for i, row in enumerate(rows, 1):
        text = str(row["prompt"]).replace("\n", " ").strip()
        lines.append(f"{i}. {text}")
    return "\n".join(lines)

def call_flash(rows):
    msg = SYSTEM_PROMPT + "\n\n" + build_msg(rows)
    for attempt in range(5):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash", contents=msg)
            raw = response.text.strip().replace("```json","").replace("```","").strip()
            return json.loads(raw)
        except Exception as e:
            err = str(e)
            if "429" in err:
                print(f"[K3] 429 — wait {RETRY_429}s (attempt {attempt+1}/5)")
                time.sleep(RETRY_429)
            elif "503" in err:
                print(f"[K3] 503 — wait {RETRY_503}s (attempt {attempt+1}/5)")
                time.sleep(RETRY_503)
            else:
                print(f"[K3] ERROR: {e}")
                break
    return None

def load_checkpoint():
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE) as f:
            return json.load(f)
    return {"last_completed_batch": BATCH_START - 1}

def save_checkpoint(idx):
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump({"last_completed_batch": idx}, f)

def flush(verified, disputed):
    if verified:
        vdf = pd.DataFrame(verified)
        if VERIFIED_FILE.exists():
            vdf.to_csv(VERIFIED_FILE, mode="a", header=False, index=False)
        else:
            vdf.to_csv(VERIFIED_FILE, index=False)
    if disputed:
        ddf = pd.DataFrame(disputed)
        if DISPUTED_FILE.exists():
            ddf.to_csv(DISPUTED_FILE, mode="a", header=False, index=False)
        else:
            ddf.to_csv(DISPUTED_FILE, index=False)

def process():
    df = pd.read_csv(INPUT_FILE)
    print(f"[K3] Loaded {len(df)} rows.")
    checkpoint = load_checkpoint()
    start = checkpoint["last_completed_batch"] + 1
    print(f"[K3] Resuming from batch {start}.")
    batches = [df.iloc[i:i+BATCH_SIZE] for i in range(0, len(df), BATCH_SIZE)]
    verified, disputed = [], []

    for batch_idx in range(start, BATCH_END + 1):
        batch = batches[batch_idx]
        rows = batch.to_dict("records")
        print(f"[K3] Batch {batch_idx+1}/892 — rows {batch.index[0]}–{batch.index[-1]}", flush=True)

        verdicts = call_flash(rows)
        if verdicts is None:
            print(f"[K3] Failed batch {batch_idx+1}. Skipping.")
            save_checkpoint(batch_idx)
            time.sleep(SLEEP)
            continue

        vmap = {item["index"]: int(item["verdict"]) for item in verdicts}
        for i, row in enumerate(rows, 1):
            fv = vmap.get(i)
            row = row.copy()
            if fv is None:
                continue
            orig = int(row.get("label", -1))
            row["flash_verdict"] = fv
            row["agreement"] = "AGREE" if fv == orig else "DISAGREE"
            if fv == orig:
                verified.append(row)
            else:
                disputed.append(row)

        save_checkpoint(batch_idx)
        if (batch_idx + 1) % 10 == 0:
            flush(verified, disputed)
            verified, disputed = [], []
            print(f"[K3] Flushed at batch {batch_idx+1}.", flush=True)
        time.sleep(SLEEP)

    flush(verified, disputed)
    print(f"[K3] Done.")

if __name__ == "__main__":
    process()
