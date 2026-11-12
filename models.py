"""
models.py — Card and Deck data structures
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional
import uuid


@dataclass
class Card:
    """A single flashcard with SM-2 scheduling metadata."""

    front: str                          # Prompt (e.g. local language word)
    back: str                           # Answer (e.g. English translation)
    transliteration: str = ""           # Romanised pronunciation (optional)
    example: str = ""                   # Example sentence (optional)

    # SM-2 fields
    card_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    easiness: float = 2.5               # EF: ease factor, min 1.3
    interval: int = 0                   # Days until next review
    repetitions: int = 0               # Consecutive correct reviews
    due_date: str = field(default_factory=lambda: date.today().isoformat())
    last_reviewed: Optional[str] = None

    def is_due(self) -> bool:
        return date.fromisoformat(self.due_date) <= date.today()

    def to_dict(self) -> dict:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, d: dict) -> "Card":
        return cls(**d)


@dataclass
class Deck:
    """A named collection of flashcards."""

    name: str
    language: str                       # e.g. "Hindi", "Punjabi", "Tamil"
    description: str = ""
    cards: list = field(default_factory=list)  # list[Card]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def due_cards(self) -> list:
        return [c for c in self.cards if c.is_due()]

    def new_cards(self) -> list:
        return [c for c in self.cards if c.repetitions == 0]

    def add_card(self, card: Card):
        self.cards.append(card)

    def remove_card(self, card_id: str) -> bool:
        before = len(self.cards)
        self.cards = [c for c in self.cards if c.card_id != card_id]
        return len(self.cards) < before

    def get_card(self, card_id: str) -> Optional[Card]:
        return next((c for c in self.cards if c.card_id == card_id), None)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "language": self.language,
            "description": self.description,
            "created_at": self.created_at,
            "cards": [c.to_dict() for c in self.cards],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Deck":
        cards = [Card.from_dict(c) for c in d.pop("cards", [])]
        deck = cls(**d)
        deck.cards = cards
        return deck
