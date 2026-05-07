"""Settings management - persist LLM config to file."""
import os
import json
import logging

logger = logging.getLogger(__name__)

SETTINGS_FILE = "/app/output/settings.json"

DEFAULT_SETTINGS = {
    "llm_api_key": "",
    "llm_api_base": "https://api.deepseek.com",
    "llm_model": "deepseek-chat",
    "vision_api_key": "",
    "vision_api_base": "",
    "vision_model": "",
}


def load_settings() -> dict:
    """Load settings from file, return merged with defaults."""
    settings = DEFAULT_SETTINGS.copy()
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                saved = json.load(f)
            settings.update(saved)
        except Exception as e:
            logger.warning(f"Failed to load settings: {e}")
    return settings


def save_settings(data: dict) -> bool:
    """Save settings to file."""
    try:
        os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
        settings = load_settings()
        settings.update(data)
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Failed to save settings: {e}")
        return False


def get_llm_config() -> dict:
    """Get LLM config for use in modules."""
    s = load_settings()
    return {
        "api_key": s["llm_api_key"],
        "api_base": s["llm_api_base"],
        "model": s["llm_model"],
        "vision_api_key": s["vision_api_key"] or s["llm_api_key"],
        "vision_api_base": s["vision_api_base"] or s["llm_api_base"],
        "vision_model": s["vision_model"] or s["llm_model"],
    }
