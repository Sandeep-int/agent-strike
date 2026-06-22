from executor.evaluator import evaluate


def test_true_positive():
    result = {"verdict": "BLOCK", "layer": "L2", "confidence": 0.99}
    out = evaluate("inject", "BLOCK", result)
    assert out["outcome"] == "TRUE_POSITIVE"
    assert out["actual"] == "BLOCK"


def test_false_negative():
    result = {"verdict": "ALLOW", "layer": "L1", "confidence": 0.1}
    out = evaluate("inject", "BLOCK", result)
    assert out["outcome"] == "FALSE_NEGATIVE"
    assert out["actual"] == "ALLOW"


def test_true_negative():
    result = {"verdict": "ALLOW", "layer": "L1", "confidence": 0.1}
    out = evaluate("what is weather", "ALLOW", result)
    assert out["outcome"] == "TRUE_NEGATIVE"


def test_false_positive():
    result = {"verdict": "BLOCK", "layer": "L2", "confidence": 0.95}
    out = evaluate("what is weather", "ALLOW", result)
    assert out["outcome"] == "FALSE_POSITIVE"


def test_unknown_verdict():
    result = {"verdict": "UNKNOWN", "layer": "NETWORK", "confidence": 0.0}
    out = evaluate("test", "BLOCK", result)
    assert out["outcome"] == "FALSE_NEGATIVE"


def test_output_fields():
    result = {"verdict": "BLOCK", "layer": "L2", "confidence": 0.99}
    out = evaluate("inject", "BLOCK", result)
    assert "prompt" in out
    assert "expected" in out
    assert "actual" in out
    assert "outcome" in out
    assert "layer" in out
    assert "confidence" in out
