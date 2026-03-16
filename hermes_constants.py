"""Shared constants for Hermes Agent.

Import-safe module with no dependencies — can be imported from anywhere
without risk of circular imports.
"""

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODELS_URL = f"{OPENROUTER_BASE_URL}/models"
OPENROUTER_CHAT_URL = f"{OPENROUTER_BASE_URL}/chat/completions"

NOUS_API_BASE_URL = "https://inference-api.nousresearch.com/v1"
NOUS_API_CHAT_URL = f"{NOUS_API_BASE_URL}/chat/completions"


def load_hermes_env() -> None:
    """Load .env files with proper encoding fallback and project fallback.
    
    Respects HERMES_HOME if set. Call this early in entry points to ensure
    env vars are available before config or other imports.
    """
    import os
    from pathlib import Path
    from dotenv import load_dotenv

    hermes_home = Path(os.getenv("HERMES_HOME", str(Path.home() / ".hermes")))
    env_path = hermes_home / ".env"
    if env_path.exists():
        try:
            load_dotenv(env_path, encoding="utf-8")
        except UnicodeDecodeError:
            load_dotenv(env_path, encoding="latin-1")
    # Fallback to local .env
    load_dotenv()
