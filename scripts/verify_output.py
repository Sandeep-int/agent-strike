import pandas as pd
from pathlib import Path

DATA_DIR = Path("/mnt/d/projects/prompt-wall/agent-strike/data")

verified = pd.read_csv(DATA_DIR / "training_data_verified.csv")
disputed = pd.read_csv(DATA_DIR / "disputed_rows_pending.csv")

print(f"=== VERIFIED ===")
print(f"Total rows     : {len(verified)}")
print(f"Label 0 (benign) : {len(verified[verified['label']==0])}")
print(f"Label 1 (attack) : {len(verified[verified['label']==1])}")
print(f"Agreement col  : {verified['agreement'].value_counts().to_dict()}")

print(f"\n=== DISPUTED ===")
print(f"Total rows     : {len(disputed)}")
print(f"DISAGREE count : {len(disputed[disputed['agreement']=='DISAGREE'])}")
print(f"SINGLE count   : {len(disputed[disputed['agreement']=='SINGLE'])}")

print(f"\n=== SAMPLE VERIFIED (5 rows) ===")
print(verified[["prompt","label","gemini_verdict","cerebras_verdict","agreement"]].head())

print(f"\n=== SAMPLE DISPUTED (5 rows) ===")
print(disputed[["prompt","label","gemini_verdict","cerebras_verdict","agreement"]].head())

print(f"\n=== DUPLICATE CHECK ===")
total = len(verified) + len(disputed)
print(f"Verified + Disputed = {total}")
orig = pd.read_csv(DATA_DIR / "final_training_dataset.csv")
print(f"Original rows      = {len(orig)}")
print(f"Duplicates in verified : {verified.duplicated(subset=['prompt']).sum()}")
print(f"Duplicates in disputed : {disputed.duplicated(subset=['prompt']).sum()}")
