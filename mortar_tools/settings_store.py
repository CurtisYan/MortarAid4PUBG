import json
import os
import sys
from dataclasses import dataclass
from typing import Iterable


@dataclass
class AppSettings:
    language: str = "en"
    start_combo_max_interval: float = 0.5


def resolve_settings_path() -> str:
    """Return the settings file path near script/executable for portable runs."""
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "settings.json")


def load_settings(path: str, allowed_intervals: Iterable[float]) -> AppSettings:
    settings = AppSettings()
    if not os.path.exists(path):
        return settings

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return settings

    lang = data.get("language")
    if isinstance(lang, str):
        settings.language = lang

    interval = data.get("start_combo_max_interval")
    if isinstance(interval, (int, float)):
        for option in allowed_intervals:
            if abs(float(interval) - float(option)) < 1e-6:
                settings.start_combo_max_interval = float(option)
                break

    return settings


def save_settings(path: str, settings: AppSettings) -> None:
    data = {
        "language": settings.language,
        "start_combo_max_interval": settings.start_combo_max_interval,
    }
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError:
        # Keep app usable even when settings cannot be written.
        pass
