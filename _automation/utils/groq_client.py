"""
Groq API Client with rate limiting and retry logic.
Shared across all agents for LLM inference.
"""

import os
import time
import json
import requests


GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# Rate limiting state
_last_request_time = 0
_rate_limit_delay = 2  # seconds between requests


def _wait_for_rate_limit():
    """Enforce minimum delay between API calls to stay within 30 RPM."""
    global _last_request_time
    now = time.time()
    elapsed = now - _last_request_time
    if elapsed < _rate_limit_delay:
        time.sleep(_rate_limit_delay - elapsed)
    _last_request_time = time.time()


def chat(
    messages: list,
    model: str = "llama-3.3-70b-versatile",
    temperature: float = 0.7,
    max_tokens: int = 4096,
    json_mode: bool = False,
    max_retries: int = 3,
) -> str:
    """
    Send a chat completion request to Groq API.
    
    Args:
        messages: List of message dicts [{"role": "...", "content": "..."}]
        model: Groq model identifier
        temperature: Sampling temperature (0.0-1.0)
        max_tokens: Maximum tokens in response
        json_mode: If True, request JSON response format
        max_retries: Number of retries on failure
    
    Returns:
        The assistant's response text
    
    Raises:
        Exception: If all retries are exhausted
    """
    if not GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY environment variable is not set. "
            "Get your free key at https://console.groq.com"
        )

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    for attempt in range(max_retries):
        _wait_for_rate_limit()

        try:
            response = requests.post(
                GROQ_API_URL,
                headers=headers,
                json=payload,
                timeout=60,
            )

            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]

            elif response.status_code == 429:
                # Rate limited — exponential backoff
                wait_time = (2 ** attempt) * 2
                print(f"  ⏳ Rate limited. Waiting {wait_time}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue

            elif response.status_code >= 500:
                # Server error — retry
                wait_time = (2 ** attempt) * 2
                print(f"  ⚠️ Server error {response.status_code}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue

            else:
                raise Exception(
                    f"Groq API error {response.status_code}: {response.text}"
                )

        except requests.exceptions.Timeout:
            print(f"  ⏱️ Request timed out (attempt {attempt + 1}/{max_retries})")
            continue
        except requests.exceptions.ConnectionError:
            print(f"  🔌 Connection error (attempt {attempt + 1}/{max_retries})")
            time.sleep(2)
            continue

    raise Exception(f"Groq API: All {max_retries} retries exhausted")


def chat_json(
    messages: list,
    model: str = "llama-3.3-70b-versatile",
    temperature: float = 0.4,
    max_tokens: int = 4096,
) -> dict:
    """
    Send a chat request and parse the response as JSON.
    Uses json_mode for structured output.
    """
    response_text = chat(
        messages=messages,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        json_mode=True,
    )

    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        # Sometimes the model wraps JSON in markdown code blocks
        cleaned = response_text.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            # Remove first and last lines (```json and ```)
            cleaned = "\n".join(lines[1:-1])
        return json.loads(cleaned)
