"""
scheduler.py — SM-2 Spaced Repetition Algorithm

Rating scale (like Anki):
    0 — Complete blackout
    1 — Wrong, but answer felt familiar
    2 — Wrong, but easy to recall on seeing the answer
    3 — Correct, but significant difficulty
    4 — Correct after a hesitation
    5 — Perfect response

Cards rated 0-2 are reset (repetitions → 0, interval → 1).
Cards rated 3-5 advance through the interval sequence.
"""

from datetime import date, timedelta
from models import Card

# Minimum ease factor — SM-2 spec
MIN_EASINESS = 1.3


def rate_card(card: Card, rating: int) -> Card:
    """
    Apply an SM-2 review rating to a card and reschedule it.

    Args:
        card:   The Card being reviewed.
        rating: Integer 0–5.

    Returns:
        The updated Card (mutated in place).
    """
    if not (0 <= rating <= 5):
        raise ValueError("Rating must be 0–5")

    card.last_reviewed = date.today().isoformat()

    if rating < 3:
        # Failed — reset sequence but keep easiness
        card.repetitions = 0
        card.interval = 1
    else:
        # Passed — advance sequence
        if card.repetitions == 0:
            card.interval = 1
        elif card.repetitions == 1:
            card.interval = 6
        else:
            card.interval = round(card.interval * card.easiness)

        card.repetitions += 1

        # Update easiness factor (SM-2 formula)
        card.easiness += 0.1 - (5 - rating) * (0.08 + (5 - rating) * 0.02)
        card.easiness = max(MIN_EASINESS, round(card.easiness, 2))

    card.due_date = (date.today() + timedelta(days=card.interval)).isoformat()
    return card


def rating_label(rating: int) -> str:
    """Human-readable label for a rating."""
    labels = {
        0: "Blackout 💀",
        1: "Wrong (familiar) 😬",
        2: "Wrong (knew it) 😅",
        3: "Hard but correct 😤",
        4: "Hesitated ✅",
        5: "Perfect! 🌟",
    }
    return labels.get(rating, str(rating))


def days_until_due(card: Card) -> int:
    delta = date.fromisoformat(card.due_date) - date.today()
    return max(0, delta.days)
