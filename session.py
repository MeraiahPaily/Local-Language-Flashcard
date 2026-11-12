"""
session.py — Interactive review session logic.
"""

import random
from models import Card, Deck
from scheduler import rate_card, rating_label
from storage import save_deck

# ANSI colour helpers
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"


def _print_card_front(card: Card, index: int, total: int):
    print(f"\n{BOLD}{'─'*50}{RESET}")
    print(f"  Card {index}/{total}")
    print(f"{BOLD}{'─'*50}{RESET}")
    print(f"\n  {CYAN}{BOLD}{card.front}{RESET}\n")
    if card.example:
        print(f"  Example: {card.example}\n")


def _print_card_back(card: Card):
    print(f"\n  {GREEN}{BOLD}Answer: {card.back}{RESET}")
    if card.transliteration:
        print(f"  Pronunciation: [{card.transliteration}]")


def _ask_rating() -> int:
    print(f"\n  How well did you remember?")
    for i in range(6):
        print(f"    {BOLD}{i}{RESET} — {rating_label(i)}")
    while True:
        try:
            r = int(input("\n  Your rating (0-5): ").strip())
            if 0 <= r <= 5:
                return r
        except ValueError:
            pass
        print(f"  {RED}Enter a number between 0 and 5.{RESET}")


def run_session(deck: Deck, limit: int = 20) -> dict:
    """
    Run a review session for all due cards in the deck.

    Returns a summary dict with session stats.
    """
    due = deck.due_cards()
    if not due:
        print(f"\n{GREEN}No cards due for review! Come back later.{RESET}")
        return {"reviewed": 0, "correct": 0, "again": []}

    random.shuffle(due)
    queue = due[:limit]

    again_queue = []   # cards rated < 3 get reviewed again this session
    results = []
    reviewed_ids = set()

    def process_queue(cards):
        for i, card in enumerate(cards, 1):
            _print_card_front(card, i, len(cards))
            input(f"  {YELLOW}[Press Enter to reveal answer]{RESET}")
            _print_card_back(card)

            rating = _ask_rating()
            rate_card(card, rating)
            results.append(rating)
            reviewed_ids.add(card.card_id)

            if rating < 3:
                again_queue.append(card)
                print(f"  {RED}↩  Will review again this session.{RESET}")
            else:
                print(f"  {GREEN}✓  Next review in {card.interval} day(s).{RESET}")

    process_queue(queue)

    if again_queue:
        print(f"\n{YELLOW}{BOLD}Reviewing {len(again_queue)} missed card(s) again…{RESET}")
        random.shuffle(again_queue)
        process_queue(again_queue)

    save_deck(deck)

    correct = sum(1 for r in results if r >= 3)
    summary = {
        "reviewed": len(reviewed_ids),
        "ratings": results,
        "correct": correct,
        "accuracy": round(correct / len(results) * 100) if results else 0,
    }
    _print_session_summary(summary)
    return summary


def _print_session_summary(s: dict):
    print(f"\n{BOLD}{'═'*50}{RESET}")
    print(f"  Session Complete!")
    print(f"{'═'*50}{RESET}")
    print(f"  Cards reviewed : {s['reviewed']}")
    print(f"  Correct        : {s['correct']}")
    print(f"  Accuracy       : {s['accuracy']}%")
    bar_filled = round(s['accuracy'] / 5)
    bar = f"{GREEN}{'█' * bar_filled}{RESET}{'░' * (20 - bar_filled)}"
    print(f"  [{bar}] {s['accuracy']}%")
    print(f"{BOLD}{'═'*50}{RESET}\n")
