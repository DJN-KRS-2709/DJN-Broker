"""
Track when we opened positions for time-based daily rotation exits.
"""
import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional

ENTRY_FILE = "storage/learning/position_entries.json"
FALLBACK_STATE = "storage/learning/daily_activity_state.json"


def _ensure_dir():
    os.makedirs(os.path.dirname(ENTRY_FILE), exist_ok=True)


def load_entries() -> Dict[str, str]:
    _ensure_dir()
    if not os.path.exists(ENTRY_FILE):
        return {}
    try:
        with open(ENTRY_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_entries(entries: Dict[str, str]) -> None:
    _ensure_dir()
    with open(ENTRY_FILE, "w") as f:
        json.dump(entries, f, indent=2)


def ensure_entry(symbol: str) -> None:
    """Record open time if missing (first time we see this position)."""
    entries = load_entries()
    if symbol not in entries:
        entries[symbol] = datetime.now(timezone.utc).isoformat()
        save_entries(entries)


def record_buy(symbol: str) -> None:
    """Call after a successful BUY order from the bot."""
    entries = load_entries()
    entries[symbol] = datetime.now(timezone.utc).isoformat()
    save_entries(entries)


def clear_symbol(symbol: str) -> None:
    entries = load_entries()
    if symbol in entries:
        del entries[symbol]
        save_entries(entries)


def hours_since_entry(symbol: str) -> Optional[float]:
    entries = load_entries()
    if symbol not in entries:
        return None
    try:
        opened = datetime.fromisoformat(entries[symbol].replace("Z", "+00:00"))
        if opened.tzinfo is None:
            opened = opened.replace(tzinfo=timezone.utc)
        delta = datetime.now(timezone.utc) - opened
        return delta.total_seconds() / 3600.0
    except (ValueError, TypeError):
        return None


def fallback_already_used_today(tz_name: str = "Europe/Berlin") -> bool:
    try:
        from zoneinfo import ZoneInfo
        today = datetime.now(ZoneInfo(tz_name)).date().isoformat()
    except Exception:
        today = datetime.now(timezone.utc).date().isoformat()
    _ensure_dir()
    if not os.path.exists(FALLBACK_STATE):
        return False
    try:
        with open(FALLBACK_STATE, "r") as f:
            st = json.load(f)
        return st.get("fallback_used_date") == today
    except (json.JSONDecodeError, OSError):
        return False


def mark_fallback_used_today(tz_name: str = "Europe/Berlin") -> None:
    try:
        from zoneinfo import ZoneInfo
        today = datetime.now(ZoneInfo(tz_name)).date().isoformat()
    except Exception:
        today = datetime.now(timezone.utc).date().isoformat()
    _ensure_dir()
    with open(FALLBACK_STATE, "w") as f:
        json.dump({"fallback_used_date": today}, f, indent=2)
