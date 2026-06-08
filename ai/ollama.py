"""
AI Integration for Documentation Generation

Uses Ollama (local LLM) to generate human-readable descriptions
for API endpoints, methods, and schemas.
"""

import requests
import subprocess
from typing import Optional


def call_ollama(prompt: str, model: str = "llama3.2:1b", timeout: int = 60) -> str:
    """
    Call Ollama API to generate text from a prompt.
    
    Args:
        prompt: The text prompt to send to the LLM.
        model: Ollama model name (default: llama3.2:1b).
        timeout: Maximum wait time in seconds.
    
    Returns:
        Generated text response, or error message if unavailable.
    """
    # Preferred method: HTTP API
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=timeout
        )
        if response.status_code == 200:
            return response.json().get("response", "").strip()
    except Exception:
        pass
    
    # Fallback method: CLI subprocess
    try:
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8',
            errors='replace'
        )
        return result.stdout.strip()
    except Exception as e:
        return f"[AI unavailable: {e}]"


def generate_description_for_endpoint(method: str, path: str, model: str = "llama3.2:1b") -> str:
    """
    Generate a one-sentence description for an API endpoint using AI.
    
    Args:
        method: HTTP method (GET, POST, etc.) or empty string for path-only.
        path: API endpoint path.
        model: Ollama model to use.
    
    Returns:
        AI-generated description.
    """
    if method:
        prompt = (
            f"Write a one-sentence description for API endpoint {method.upper()} {path}. "
            "Be clear and concise. Do not include the HTTP method in the description."
        )
    else:
        prompt = (
            f"Write a one-sentence description for API endpoint {path}. "
            "Be clear and concise."
        )
    
    return call_ollama(prompt, model=model)