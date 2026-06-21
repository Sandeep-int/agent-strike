def evaluate(prompt: str, expected: str, result: dict) -> dict:
    verdict = result.get("verdict", "UNKNOWN")
    actual = "BLOCK" if verdict == "BLOCK" else "ALLOW"

    if expected == "BLOCK" and actual == "BLOCK":
        outcome = "TRUE_POSITIVE"
    elif expected == "BLOCK" and actual == "ALLOW":
        outcome = "FALSE_NEGATIVE"
    elif expected == "ALLOW" and actual == "ALLOW":
        outcome = "TRUE_NEGATIVE"
    elif expected == "ALLOW" and actual == "BLOCK":
        outcome = "FALSE_POSITIVE"
    else:
        outcome = "UNKNOWN"

    return {
        "prompt": prompt,
        "expected": expected,
        "actual": actual,
        "outcome": outcome,
        "layer": result.get("layer", "UNKNOWN"),
        "confidence": result.get("confidence", 0.0)
    }
