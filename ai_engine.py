# ai_engine.py
import os
import json
import requests
import time

from typing import Optional

# Simple fallback rule-based outputs
def fallback_response(command: str) -> str:
    cmd = command.strip().lower()
    if cmd in ("ls", "ls -la", "dir"):
        return "README.txt  config.json  logs  honeypot.py"
    if cmd.startswith("cd "):
        target = cmd[3:].strip() or "/home"
        return f"Changed directory to {target}"
    if cmd.startswith("cat ") or cmd.startswith("type "):
        return "This is sample file content. (simulated)"
    if cmd in ("pwd", "cwd"):
        return "/home/guest"
    if cmd == "whoami":
        return "guest"
    if "sudo" in cmd or "su " in cmd:
        return "Sorry, user is not in the sudoers file. This incident will be reported."
    return f"bash: {command}: command not found"

# Ollama local server attempt
def ollama_generate(prompt: str, config: dict) -> Optional[str]:
    try:
        base = config.get("ollama_url", "http://localhost:11434")
        model = config.get("ollama_model", "llama3")
        url = f"{base}/api/generate"
        payload = {"model": model, "prompt": prompt, "max_tokens": 200}
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            # Ollama streaming vs static responses vary; handle common structure
            if isinstance(data, dict):
                # expected field could be 'text' or 'response'
                return data.get("response") or data.get("text") or json.dumps(data)
            return str(data)
        else:
            # not available or error
            return None
    except Exception:
        return None

# OpenAI via requests to their completion endpoint (simple)
def openai_generate(prompt: str, config: dict) -> Optional[str]:
    try:
        import openai
    except Exception:
        return None
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return None
    try:
        openai.api_key = key
        model = config.get("openai_model", "gpt-3.5-turbo")
        # Use chat completions
        resp = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a Linux-like terminal. Respond exactly like terminal output would."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.2,
            n=1
        )
        return resp.choices[0].message["content"].strip()
    except Exception:
        return None

# Unified generate function
def generate_ai_response(command: str, config: dict) -> str:
    """
    Tries Ollama (local), then OpenAI (API key), then falls back to simple rule-based output.
    """
    # Build a concise terminal-like prompt
    prompt = (
        f"You are an Ubuntu 20.04 terminal. The user typed:\n{command}\n\n"
        "Return the exact terminal output (short, realistic). Do not say you are an AI."
    )

    # 1) Try Ollama (local)
    if config.get("use_ai", True):
        out = ollama_generate(prompt, config.get("ai", {}))
        if out:
            return out.strip()

    # 2) Try OpenAI (if API key available)
    out = openai_generate(prompt, config.get("ai", {}))
    if out:
        return out.strip()

    # 3) Fallback
    return fallback_response(command)