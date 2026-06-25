import httpx
import time
import config

HEADERS = {
    "X-API-Key": config.AGENT_STRIKE_INTERNAL_KEY,
    "Content-Type": "application/json"
}

MAX_RETRIES = 3
RETRY_DELAYS = [2, 5, 10]  # seconds between retries

def fire(prompt: str) -> dict:
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            response = httpx.post(
                f"{config.AGENT_SHIELD_URL}/v1/check",
                headers=HEADERS,
                json={"prompt": prompt},
                timeout=30.0
            )
            data = response.json()
            return {
                "verdict": data.get("verdict", "UNKNOWN"),
                "layer": data.get("layer", "UNKNOWN"),
                "confidence": data.get("confidence", 0.0),
                "status_code": response.status_code
            }
        except Exception as e:
            last_error = str(e)
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAYS[attempt])
            continue

    return {
        "verdict": "ERROR",
        "layer": "NETWORK",
        "confidence": 0.0,
        "status_code": 0,
        "error": last_error
    }
