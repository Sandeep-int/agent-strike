<p align="center">
  <img src="https://raw.githubusercontent.com/Sandeep-int/agent-strike/main/assets/banner.png" alt="Agent Strike" width="800"/>
</p>

---

**Autonomous adversarial red-team framework for [Agent Shield](https://github.com/Sandeep-int/agent-shield).**

Multi-agent · LLM-generated attacks · Garak-integrated · Self-improving · CI-gated

<div align="center">

[![Tests](https://img.shields.io/badge/Tests-15%20Passing-22c55e?style=for-the-badge&logo=github)](https://github.com/Sandeep-int/agent-strike/actions)
[![Bandit](https://img.shields.io/badge/Bandit-Clean-22c55e?style=for-the-badge)](https://github.com/Sandeep-int/agent-strike)
[![SonarCloud](https://img.shields.io/badge/SonarCloud-Connected-4E9BCD?style=for-the-badge&logo=sonarcloud&logoColor=white)](https://sonarcloud.io)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue?style=for-the-badge)](./LICENSE)

</div>

---

## What This Is

Agent Strike is the adversarial testing engine behind Agent Shield's detection
accuracy claims. It runs three attack sources against the live Shield API —
hardcoded payloads, industry-standard Garak probes, and a **CrewAI-based agent
that generates novel attacks autonomously** — then measures what gets through.

Every accuracy number in Shield's README traces back to a run logged here.

**Current status: autonomous attack generation is live.** A Red Team agent
generates and fires attacks without a hardcoded prompt list. Scheduling and
full self-retraining are not yet automated — see Roadmap.

---

## Process — How an Attack Run Works

RedTeamAgent (CrewAI + Groq/Qwen3-32B)

↓

Generate novel attack prompt (10 categories — no template, LLM-authored)

↓

shield_caller.py → fire at Agent Shield /v1/check

↓

Evaluate verdict: TP / FP / TN / FN

↓

result_logger.py → agent_results.csv (every attempt)

↓

ALLOW verdict (false negative)? → missed_samples.csv

↓

blindspot_detector.py reads missed_samples.csv

↓

Generates harder mutated variant of each miss (variants_per_miss)

↓

Re-fires mutation at Shield → loop continues

Garak runs separately, on demand, for broad probe-family coverage (9 attack
families) — the agent loop above is for continuous, novel attack generation
the static Garak suite can't produce on its own.

---

## Architecture

| Module | Purpose |
|--------|---------|
| `agents/red_team_agent.py` | CrewAI agent — generates + fires novel attacks |
| `agents/tools/attack_generator.py` | Groq direct API attack generation (`reasoning_effort: none`) |
| `agents/tools/shield_caller.py` | Fires prompts at Shield, returns verdict |
| `agents/result_logger.py` | Logs every verdict to `agent_results.csv` / `missed_samples.csv` |
| `agents/blindspot_detector.py` | Reads misses, generates harder mutations, re-tests |
| `attacks/` | Hardcoded attack prompt library (legacy baseline) |
| `garak/` | Garak red-team probe config + results |
| `data/` | Local, gitignored — training datasets and CSV logs live here |

**Two isolated environments — do not mix:**

| Venv | Python | Used by |
|---|---|---|
| `venv/` | 3.14.4 | Hardcoded attacks, Garak, legacy test suite |
| `agents/venv/` | 3.11.15 | CrewAI agents (`crewai==1.14.4` pinned — newer versions break Groq) |

---

## Detection Results

**Two result sets — different test methods, both real.**

### Legacy manual baseline (hardcoded + Garak, 76 prompts)

| Metric | Result |
|--------|--------|
| True Positives | 98% |
| False Negatives | 2% |
| True Negatives | 96% |
| False Positives | 4% |

Small sample by design — validates regression after rule/model changes, not
statistical significance.

### Autonomous agent run (RedTeamAgent, novel LLM-generated attacks)

| Metric | Result |
|--------|--------|
| Total requests fired | 40,000+ |
| Blocked | 11,700+ |
| Block rate | 29.3% |
| Avg latency | ~1,553ms |

Lower block rate is expected and intentional — these are novel, unscripted
attacks designed to find gaps the hardcoded/Garak baseline can't reach. Every
miss here becomes a `missed_samples.csv` entry for the blindspot loop.

---

## Garak Probe Coverage — All 9 Families Run

| Probe Family | FN Rate | Status |
|---|---|---|
| `dan` | 0% | ✅ Strong |
| `promptinject` | ~4% | ✅ Strong |
| `goodside` | 0% | ✅ Fixed — Unicode Tag decode (PR #54) |
| `encoding` (Base64/Hex/ROT13) | 9–21% | ⚠️ L4 has decoders, partial leakage — retrain target |
| `encoding` (NATO/Ecoji/Braille/Atbash/Zalgo) | — | ✅ Decoders shipped (PR #63) — re-measure pending |
| `latentinjection` (RAG) | 90–92% | ❌ Biggest blind spot — retest pending post mDeBERTa retrain |
| `LatentJailbreak` | 73–75% | ❌ Blind spot — retrain priority |
| `smuggling` | 0% | ✅ Fixed — hypothetical/rewrite patterns (PR #56) |
| `web_injection` | ~4% | ✅ Acceptable — markdown URI exfil only |
| `suffix` (GCG) | 0% | ✅ Strong |
| `sysprompt_extraction` | — | ⏭️ Skipped — incompatible with REST generator |

---

## Dataset Work

Strike isn't just a test runner — it builds Shield's training data.

| Dataset | Rows | Status |
|---|---|---|
| `final_training_dataset.csv` (Garak misses + Alpaca benign, 50/50) | 44,574 | ✅ Used in Day 20 fine-tune |
| Track A — 311k row cleaning (DeepSeek + Groq two-pass judge) | 311,497 | ⏳ Paused — DeepSeek migration pending |

Benign side was collected by firing Alpaca instructions through Shield and
recording real ALLOW verdicts — confirmed Shield's L2 classifier was
over-blocking benign text before fine-tuning.

---

## CI/CD

| Check | Status |
|---|---|
| pytest (Strike core) | 15 tests passing |
| Bandit (SAST) | Clean |
| pip-audit | Enabled |
| Branch protection | `main`, enforced |
| SonarCloud | Connected |
| CodeRabbit | Auto-review on PR |
| Dependabot | Enabled |

---

## Roadmap — Path to Full Autonomy

| Stage | Item | Status |
|---|---|---|
| 1 | Red Team agent — autonomous attack generation | ✅ Live |
| 2 | Result logging (TP/FP/FN/TN → CSV) | ✅ Live |
| 3 | Blindspot detector — miss → mutation → re-test loop | ✅ Built, awaiting real-FN validation |
| 4 | Blue Team agent — automated defense patching | ⏳ Not started |
| 5 | Analyst agent — full pipeline reporting | ⏳ Not started |
| 6 | Azure Function scheduled run (2AM nightly, no manual trigger) | ⏳ Not started |
| 7 | Auto-trigger Kaggle retrain when miss rate > threshold | ⏳ Not started |
| 8 | Track A full Pass 1 (DeepSeek, 311k rows) | ⏳ Paused |
| 9 | Track A Pass 2 (Groq dispute resolution) | ⏳ Blocked on Pass 1 |
| 10 | 5-language translation (Hindi, Bengali, Marathi, Telugu, Tamil) | ⏳ Blocked behind Track A |

**End state:** Shield attacks itself nightly without a human starting the run,
without a human writing the attack, and without a human deciding when to
retrain — humans review the retrain decision, not generate the data for it.

---

## Security

- No production keys in this repo.
- All secrets via environment variables only
- Internal key auth required — Strike traffic never mixes with public Shield metrics
- See [SECURITY.md](SECURITY.md) for vulnerability reporting

---

## Related

- [Agent Shield](https://github.com/Sandeep-int/agent-shield) — the production API being tested
- [Garak](https://github.com/NVIDIA/garak) — NVIDIA's LLM red-team framework, used for probe coverage
- [CrewAI](https://github.com/crewAIInc/crewAI) — multi-agent orchestration framework powering the Red Team agent

---

## License

Apache 2.0 — see [LICENSE](./LICENSE) for details.

---
<div align="center">

Built by [Sandeep S](https://github.com/Sandeep-int) &nbsp;|&nbsp;
[LinkedIn](https://www.linkedin.com/in/sandeep-int/)

</div>
