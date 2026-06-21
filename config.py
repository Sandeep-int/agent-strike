import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
AGENT_STRIKE_INTERNAL_KEY = os.getenv("AGENT_STRIKE_INTERNAL_KEY")
AGENT_SHIELD_URL = os.getenv("AGENT_SHIELD_URL")
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_TABLE_NAME = os.getenv("AZURE_TABLE_NAME", "agentstrikeresults")

# Thresholds
MISS_RATE_THRESHOLD = 0.05   # 5% — alert if exceeded
FP_RATE_THRESHOLD = 0.02     # 2% — alert if exceeded
ATTACKS_PER_RUN = 50         # prompts generated per run
