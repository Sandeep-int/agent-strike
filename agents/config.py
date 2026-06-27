import os
from dotenv import load_dotenv
load_dotenv("/mnt/d/projects/prompt-wall/agent-strike/.env")

# Groq (primary — faster, no Venice block)
GROQ_API_KEY = os.getenv("AGENT_STRIKE_GROQ_KEY")
GROQ_MODEL = "qwen/qwen3-32b"
GROQ_FALLBACK_MODEL = "llama-3.3-70b-versatile"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

# OpenRouter (kept for reference — not used by agent)
OPENROUTER_API_KEY = os.getenv("AGENT_SHIELD_OPENROUTER_KEY")
OPENROUTER_MODEL = "z-ai/glm-4.5-air:free"
OPENROUTER_FALLBACK_MODEL = "z-ai/glm-4.5-air:free"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Shield target
SHIELD_ENDPOINT = "https://agent-shield-chbxh2hkhxgucgax.eastasia-01.azurewebsites.net/v1/check"
SHIELD_API_KEY = os.getenv("AGENT_STRIKE_INTERNAL_KEY")

# Fail fast if keys missing
if not GROQ_API_KEY:
    raise ValueError("AGENT_STRIKE_GROQ_KEY not found in .env")
if not SHIELD_API_KEY:
    raise ValueError("AGENT_STRIKE_INTERNAL_KEY not found in .env")
