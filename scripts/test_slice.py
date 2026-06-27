import pandas as pd
from pathlib import Path

DATA_DIR = Path("/mnt/d/projects/prompt-wall/agent-strike/data")
df = pd.read_csv(DATA_DIR / "final_training_dataset.csv")
df.head(100).to_csv(DATA_DIR / "test_100.csv", index=False)
print(f"Saved 100 rows to test_100.csv")
