import time
import requests

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

MAX_RETRIES = 3
RETRY_DELAYS = [2, 5, 10]


def call_shield(prompt: str, category: str = "unknown") -> dict:
    """
    Fires a single prompt at the Shield API.
    Returns a verdict dict. Does NOT log to disk — caller's job.

    Returns:
        {
            "prompt": str,
            "category": str,
            "verdict": "BLOCK" | "ALLOW" | "NETWORK_ERROR",
            "layer": str | None,
            "latency_ms": float | None,
            "raw_response": dict | None,
            "error": str | None,
        }
    """
    headers = {
        "X-API-Key": config.SHIELD_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {"prompt": prompt}

    last_error = None

    for attempt in range(MAX_RETRIES):
        try:
            start = time.time()
            resp = requests.post(
                config.SHIELD_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=15,
            )
            latency_ms = (time.time() - start) * 1000

            if resp.status_code == 200:
                data = resp.json()
                return {
                    "prompt": prompt,
                    "category": category,
                    "verdict": data.get("verdict", "UNKNOWN"),
                    "layer": data.get("layer_hit", None),
                    "latency_ms": round(latency_ms, 2),
                    "raw_response": data,
                    "error": None,
                }
            elif resp.status_code == 422:
                return {
                    "prompt": prompt,
                    "category": category,
                    "verdict": "REJECTED_422",
                    "layer": None,
                    "latency_ms": round(latency_ms, 2),
                    "raw_response": None,
                    "error": "422: payload exceeds 2000-char limit",
                }
            else:
                last_error = f"HTTP {resp.status_code}: {resp.text[:200]}"

        except requests.exceptions.RequestException as e:
            last_error = str(e)

        if attempt < MAX_RETRIES - 1:
            time.sleep(RETRY_DELAYS[attempt])

    return {
        "prompt": prompt,
        "category": category,
        "verdict": "NETWORK_ERROR",
        "layer": None,
        "latency_ms": None,
        "raw_response": None,
        "error": last_error,
    }
