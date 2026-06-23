<p align="center">
  <img src="https://raw.githubusercontent.com/Sandeep-int/agent-strike/main/assets/banner.png" alt="Agent Strike" width="800"/>
</p>

---

**Automated adversarial red-team framework for [Agent Shield](https://github.com/Sandeep-int/agent-shield).**

Open source · Local-first · Garak-integrated · CI-gated

<div align="center">

[![Tests](https://img.shields.io/badge/Tests-15%20Passing-22c55e?style=for-the-badge&logo=github)](https://github.com/Sandeep-int/agent-strike/actions)
[![Bandit](https://img.shields.io/badge/Bandit-Clean-22c55e?style=for-the-badge)](https://github.com/Sandeep-int/agent-strike)
[![SonarCloud](https://img.shields.io/badge/SonarCloud-Connected-4E9BCD?style=for-the-badge&logo=sonarcloud&logoColor=white)](https://sonarcloud.io)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue?style=for-the-badge)](./LICENSE)

</div>

---

## What This Is

Agent Strike is the adversarial testing engine behind Agent Shield's detection
accuracy claims. It fires real attack payloads — hardcoded, LLM-generated, and
industry-standard Garak probes — at the live Shield API and measures what gets
through.

Every accuracy number in Shield's README traces back to a run logged here.

**Current status: local-only, on-demand.** Strike runs manually from a developer
machine. It is not yet scheduled or autonomous — see Roadmap below.

---

## Pipeline

```
Attack Generator (hardcoded + Groq LLM + Garak probes)
        ↓
Fire at Agent Shield /v1/check (internal key, no rate limit)
        ↓
Evaluate verdict: TP / FP / TN / FN
        ↓
Log to Azure Table (agentstriketraffic / agentstrikeresults)
        ↓
Flag misses → feed into fine-tune dataset
```

---

## Architecture

| Module | Purpose |
|--------|---------|
| `attacks/` | Hardcoded attack prompt library |
| `core/` | Groq LLM attack generator |
| `executor/` | Fires prompts at Shield, evaluates verdicts |
| `reporter/` | Logs results to Azure Table, threshold alerts |
| `scripts/` | Dataset collection, training feed builders |
| `garak/` | Garak red-team probe config + results |
| `data/` | Local, gitignored — training datasets live here |

---

## Detection Results

**Latest clean run — 76 prompts, manual local execution.**

| Metric | Result |
|--------|--------|
| True Positives | 98% |
| False Negatives | 2% |
| True Negatives | 96% |
| False Positives | 4% |

Small sample size by design — this run validates regression after rule/model
changes, not statistical significance. Full Garak suite (below) is the broader
coverage check.

---

## Garak Probe Coverage — All 9 Families Run

| Probe Family | FN Rate | Status |
|---|---|---|
| `dan` | 0% | ✅ Strong |
| `promptinject` | ~4% | ✅ Strong |
| `goodside` | 0% | ✅ Fixed — Unicode Tag decode (PR #54) |
| `encoding` (Base64/Hex/ROT13) | 9–21% | ⚠️ L4 has decoders, partial leakage — retrain target |
| `encoding` (NATO/Ecoji/Braille/Atbash/Zalgo) | up to 64% | ❌ No decoder — retrain priority |
| `latentinjection` (RAG) | 90–92% | ❌ Biggest blind spot — retrain priority #1 |
| `LatentJailbreak` | 73–75% | ❌ Blind spot — retrain priority #2 |
| `smuggling` | 0% | ✅ Fixed — hypothetical/rewrite patterns (PR #56) |
| `web_injection` | ~4% | ✅ Acceptable — markdown URI exfil only |
| `suffix` (GCG) | 0% | ✅ Strong |
| `sysprompt_extraction` | — | ⏭️ Skipped — incompatible with REST generator |

---

## Dataset Work

Strike isn't just a test runner — it builds Shield's training data.

| Dataset | Rows | Status |
|---|---|---|
| `final_training_dataset.csv` (Garak misses + Alpaca benign, 50/50) | 44,574 | ✅ Ready for fine-tune |
| Track A — 311k row cleaning (DeepSeek + Groq two-pass judge) | 311,497 | ⏳ Paused — DeepSeek migration pending |

Benign side was collected by firing 23,412 Alpaca instructions through Shield
and recording real ALLOW verdicts — confirmed Shield's L2 classifier was
over-blocking benign text at a 9.7% false-positive rate before fine-tuning.

---

## CI/CD

| Check | Status |
|---|---|
| pytest | 15 tests passing |
| Bandit (SAST) | Clean |
| pip-audit | Enabled |
| Branch protection | `main`, enforced |
| SonarCloud | Connected |
| CodeRabbit | Auto-review on PR |
| Dependabot | Enabled |

---

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
| `AGENT_STRIKE_INTERNAL_KEY` | Strike's internal auth key for Shield (bypasses rate limit) |
| `AGENT_SHIELD_URL` | Shield API base URL |
| `GROQ_API_KEY` | Groq key for LLM attack generation |
| `AGENT_SHIELD_DATASET_GEN_DEEPSEEK_KEY` | DeepSeek key for Track A dataset judging (Pass 1) |
| `AZURE_STORAGE_CONNECTION_STRING` | Azure Table logging |
| `AZURE_TABLE_NAME` | Results table name |

---

## Roadmap

| Item | Status |
|---|---|
| Manual local execution | ✅ Current |
| Azure Function scheduled run (2AM nightly) | ⏳ Not started |
| Auto-trigger Kaggle retrain when miss rate > 5% | ⏳ Not started |
| Track A full Pass 1 (DeepSeek, 311k rows) | ⏳ Paused |
| Track A Pass 2 (Groq dispute resolution) | ⏳ Blocked on Pass 1 |
| 5-language translation (Hindi, Bengali, Marathi, Telugu, Tamil) | ⏳ Blocked behind Track A |

---

## Security

- No production keys in this repo
- All secrets via environment variables only
- Internal key auth required — Strike traffic never mixes with public Shield metrics
- See [SECURITY.md](SECURITY.md) for vulnerability reporting

---

## Related

- [Agent Shield](https://github.com/Sandeep-int/agent-shield) — the production API being tested
- [Garak](https://github.com/NVIDIA/garak) — NVIDIA's LLM red-team framework, used for probe coverage

---

## License

Apache 2.0 — see [LICENSE](./LICENSE) for details.

---
<div align="center">

Built by [Sandeep S](https://github.com/Sandeep-int) &nbsp;|&nbsp;
[LinkedIn](https://www.linkedin.com/in/sandeep-int/)

</div>
