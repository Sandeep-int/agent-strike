import httpx
import config

HEADERS = {
    "X-API-Key": config.AGENT_STRIKE_INTERNAL_KEY,
    "Content-Type": "application/json"
}

def fire(prompt: str) -> dict:
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
        return {
            "verdict": "ERROR",
            "layer": "NETWORK",
            "confidence": 0.0,
            "status_code": 0
        }
