import datetime
from attacks.hardcoded import ATTACK_PROMPTS, BENIGN_PROMPTS
from core.llm_attacker import generate_attacks, generate_benign
from executor.shield_caller import fire
from executor.evaluator import evaluate
from reporter.results_logger import save_csv, save_azure
from reporter.alert import check_thresholds

def run():
    print("="*60)
    print("AGENT STRIKE — Starting Run")
    print(f"Time: {datetime.datetime.now()}")
    print("="*60)

    # Step 1 — Collect all prompts
    print("\n[1] Generating attacks via Groq/Llama3...")
    all_prompts = []
    all_prompts += ATTACK_PROMPTS
    all_prompts += BENIGN_PROMPTS

    try:
        all_prompts += generate_attacks()
        all_prompts += generate_benign()
        print(f"    Llama3 generated attacks added")
    except Exception as e:
        print(f"    Llama3 failed: {e} — using hardcoded only")

    print(f"    Total prompts: {len(all_prompts)}")

    # Step 2 — Fire at Agent Shield
    print("\n[2] Firing at Agent Shield...")
    results = []
    for i, item in enumerate(all_prompts):
        result = fire(item["prompt"])
        evaluated = evaluate(item["prompt"], item["expected"], result)
        results.append(evaluated)
        print(f"    [{i+1}/{len(all_prompts)}] {evaluated['outcome']} — {item['prompt'][:50]}")

    # Step 3 — Calculate stats
    print("\n[3] Calculating results...")
    total = len(results)
    tp = sum(1 for r in results if r["outcome"] == "TRUE_POSITIVE")
    fn = sum(1 for r in results if r["outcome"] == "FALSE_NEGATIVE")
    tn = sum(1 for r in results if r["outcome"] == "TRUE_NEGATIVE")
    fp = sum(1 for r in results if r["outcome"] == "FALSE_POSITIVE")

    attacks_total = tp + fn
    benign_total = tn + fp

    miss_rate = fn / attacks_total if attacks_total > 0 else 0
    fp_rate = fp / benign_total if benign_total > 0 else 0

    stats = {
        "total": total,
        "true_positive": tp,
        "false_negative": fn,
        "true_negative": tn,
        "false_positive": fp,
        "miss_rate": miss_rate,
        "fp_rate": fp_rate
    }

    # Step 4 — Print report
    print("\n" + "="*60)
    print("AGENT STRIKE REPORT")
    print("="*60)
    print(f"Total prompts fired : {total}")
    print(f"TRUE POSITIVES      : {tp}/{attacks_total} ({(tp/attacks_total*100) if attacks_total else 0:.1f}%)")
    print(f"FALSE NEGATIVES     : {fn}/{attacks_total} ({miss_rate*100:.1f}%) ← missed attacks")
    print(f"TRUE NEGATIVES      : {tn}/{benign_total} ({(tn/benign_total*100) if benign_total else 0:.1f}%)")
    print(f"FALSE POSITIVES     : {fp}/{benign_total} ({fp_rate*100:.1f}%) ← over-blocking")

    # Step 5 — Save results
    print("\n[4] Saving results...")
    save_csv(results)
    save_azure(results)

    # Step 6 — Check thresholds
    print("\n[5] Checking thresholds...")
    check_thresholds(stats)

    print("\nDone.")

if __name__ == "__main__":
    run()
