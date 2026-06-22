# Agent Strike

Internal adversarial testing framework for [Agent Shield](https://github.com/Sandeep-int/agent-shield).

## What It Does

Agent Strike automatically fires attack prompts at Agent Shield and measures detection accuracy.
Attack Generator (hardcoded + Groq LLM)

↓

Fire at Agent Shield /v1/check

↓

Evaluate: TP / FP / TN / FN

↓

Log results + trigger alerts if thresholds exceeded
## Architecture

| Module | Purpose |
|--------|---------|
| `attacks/` | Hardcoded attack prompt library |
| `core/` | Groq LLM attack generator |
| `executor/` | Fires prompts at Shield, evaluates results |
| `reporter/` | Logs results, triggers threshold alerts |
| `scripts/` | Data collection and training feed scripts |
| `garak/` | Garak red-team probe config for Shield |

## Detection Results (Latest Run)

| Metric | Result |
|--------|--------|
| True Positives | 98% |
| False Negatives | 2% |
| True Negatives | 96% |
| False Positives | 4% |

## Garak Probe Coverage

| Probe Family | FN Rate | Status |
|---|---|---|
| `dan` | 0% | ✅ Strong |
| `promptinject` | 4% | ✅ Strong |
| `goodside` | 0% | ✅ Fixed (PR #54) |
| `encoding` | 5–64% | ⚠️ Partial |
| `latentinjection` | 92% | ❌ Blind spot |
| `smuggling` | 0% | ✅ Fixed (PR #56) |
| `web_injection` | 4% | ✅ Acceptable |
| `suffix` | 0% | ✅ Strong |

## Setup

```bash
git clone https://github.com/Sandeep-int/agent-strike
cd agent-strike
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # add your keys
python3 main.py
```

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `AGENT_STRIKE_INTERNAL_KEY` | Strike's internal auth key for Shield |
| `AGENT_SHIELD_URL` | Shield API base URL |
| `GROQ_API_KEY` | Groq key for LLM attack generation |
| `AZURE_STORAGE_CONNECTION_STRING` | Azure Table logging |
| `AZURE_TABLE_NAME` | Results table name |

## Security

- No production keys in this repo
- All secrets via environment variables only
- See [SECURITY.md](SECURITY.md) for vulnerability reporting

## Related

- [Agent Shield](https://github.com/Sandeep-int/agent-shield) — the production API being tested
- [Garak](https://github.com/NVIDIA/garak) — LLM red-team framework used for probe testing

## License

Apache 2.0
