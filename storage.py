"""
storage.py — Save and load decks as JSON files.
"""

import json
import os
from pathlib import Path
from models import Deck

DATA_DIR = Path(__file__).parent / "data"


def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def deck_path(name: str) -> Path:
    safe = name.replace(" ", "_").lower()
    return DATA_DIR / f"{safe}.json"


def save_deck(deck: Deck):
    ensure_data_dir()
    path = deck_path(deck.name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(deck.to_dict(), f, ensure_ascii=False, indent=2)


def load_deck(name: str) -> Deck:
    path = deck_path(name)
    if not path.exists():
        raise FileNotFoundError(f"Deck '{name}' not found at {path}")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return Deck.from_dict(data)


def list_decks() -> list[str]:
    ensure_data_dir()
    return [
        f.stem.replace("_", " ").title()
        for f in DATA_DIR.glob("*.json")
    ]


def delete_deck(name: str) -> bool:
    path = deck_path(name)
    if path.exists():
        os.remove(path)
        return True
    return False
