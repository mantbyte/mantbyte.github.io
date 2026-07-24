import logging
import time
import json
import random
import re
from google import genai
from google.genai import types
from google.genai.errors import APIError
from _ai.config import GEMINI_API_KEY, AI_CONFIG

# Configure structured logging
logger = logging.getLogger("ai_provider")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '{"time": "%(asctime)s", "agent": "%(agent)s", "level": "%(levelname)s", "message": "%(message)s"}'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

def _exponential_backoff(attempt: int) -> float:
    """Calculate delay with exponential backoff and jitter."""
    base_delay = AI_CONFIG.get("rate_limit_delay_seconds", 2)
    max_delay = 60
    delay = min(base_delay * (2 ** attempt), max_delay)
    jitter = random.uniform(0, 0.1 * delay)
    return delay + jitter

def _execute_with_retry(agent_name: str, func, *args, **kwargs):
    """Execute an API call with robust retry logic and model fallback."""
    if not client:
        raise RuntimeError("GEMINI_API_KEY is not set.")

    max_retries = AI_CONFIG.get("max_retries", 3)
    
    # Try multiple standard models in case of 404 (deprecated) or 429 (out of quota)
    # The first model is whatever is passed in kwargs, then we fallback
    base_model = kwargs.get("model", "gemini-3.0-flash")
    fallback_models = [
        base_model, 
        "gemini-flash-latest",
        "gemini-pro-latest",
        "gemini-2.5-pro",
        "gemini-2.5-flash-lite",
        "gemini-3-flash-preview",
        "gemini-3.5-flash-lite",
        "gemini-3.0-flash", 
        "gemini-3.1-flash", 
        "gemini-3.5-flash", 
        "gemini-2.0-flash", 
        "gemini-1.5-pro", 
        "gemini-3.6-flash"
    ]
    
    # Deduplicate while preserving order
    models_to_try = []
    for m in fallback_models:
        if m not in models_to_try:
            models_to_try.append(m)

    last_error = None
    
    for model_name in models_to_try:
        kwargs["model"] = model_name
        print(f"  🤖 Trying model: {model_name} for agent {agent_name}...")
        
        for attempt in range(max_retries + 1):
            try:
                start_time = time.time()
                response = func(*args, **kwargs)
                duration = time.time() - start_time
                
                token_count = "unknown"
                if hasattr(response, 'usage_metadata') and response.usage_metadata:
                    token_count = response.usage_metadata.total_token_count
                    
                logger.info(f"Generated text | duration={duration:.2f}s | tokens={token_count}", extra={"agent": agent_name})
                return response.text
                
            except APIError as e:
                status_code = e.code if hasattr(e, 'code') else 500
                last_error = e
                
                if status_code == 404:
                    print(f"  ⚠️ Model {model_name} is deprecated (404). Falling back...")
                    break # Break retry loop, try next model
                    
                if status_code == 429:
                    print(f"  ⚠️ Model {model_name} hit quota limit (429). Falling back...")
                    break # Break retry loop, try next model

                if status_code in (500, 502, 503, 504):
                    if attempt == max_retries:
                        print(f"  ⚠️ Server error on {model_name} after {max_retries} retries. Falling back...")
                        break # Try next model
                    delay = _exponential_backoff(attempt)
                    logger.warning(f"Retry {attempt + 1}/{max_retries} for status {status_code}. Waiting {delay:.2f}s", extra={"agent": agent_name})
                    time.sleep(delay)
                else:
                    logger.error(f"Unrecoverable API error: {str(e)}", extra={"agent": agent_name})
                    raise
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}", extra={"agent": agent_name})
                raise
                
    raise RuntimeError(f"All fallback models failed. Last error: {str(last_error)}")

def generate(agent_name: str, system_instruction: str, user_prompt: str, temperature: float = 0.7, max_output_tokens: int = 8192) -> str:
    """Generate plain text (Markdown) response."""
    model = AI_CONFIG.get("model", "gemini-2.5-flash")
    
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
    )
    
    return _execute_with_retry(
        agent_name,
        client.models.generate_content,
        model=model,
        contents=user_prompt,
        config=config
    )

def generate_json(agent_name: str, system_instruction: str, user_prompt: str, temperature: float = 0.3) -> dict:
    """Generate JSON response and parse it robustly."""
    model = AI_CONFIG.get("model", "gemini-2.5-flash")
    
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=temperature,
        response_mime_type="application/json",
    )
    
    raw_text = _execute_with_retry(
        agent_name,
        client.models.generate_content,
        model=model,
        contents=user_prompt,
        config=config
    )
    
    # Robust parsing to handle markdown fences and extra text
    cleaned = raw_text.strip()
    
    # Extract content between ``` if present
    match = re.search(r'```(?:json)?\s*(.*?)\s*```', cleaned, re.DOTALL)
    if match:
        cleaned = match.group(1).strip()
        
    # Extract outermost JSON object or array to strip any remaining garbage text
    start_brace = cleaned.find('{')
    start_bracket = cleaned.find('[')
    
    start_idx = -1
    if start_brace != -1 and start_bracket != -1:
        start_idx = min(start_brace, start_bracket)
    elif start_brace != -1:
        start_idx = start_brace
    else:
        start_idx = start_bracket
        
    if start_idx != -1:
        end_char = '}' if cleaned[start_idx] == '{' else ']'
        end_idx = cleaned.rfind(end_char)
        if end_idx != -1:
            cleaned = cleaned[start_idx:end_idx+1]
    
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON. Raw output: {raw_text}", extra={"agent": agent_name})
        raise ValueError(f"Agent {agent_name} produced invalid JSON: {str(e)}")

def generate_markdown(agent_name: str, system_instruction: str, user_prompt: str) -> str:
    """Alias for generate() optimized for markdown generation."""
    return generate(agent_name, system_instruction, user_prompt, temperature=0.7)

def review(agent_name: str, system_instruction: str, user_prompt: str) -> dict:
    """Alias for generate_json() optimized for reviewing."""
    return generate_json(agent_name, system_instruction, user_prompt, temperature=0.2)
