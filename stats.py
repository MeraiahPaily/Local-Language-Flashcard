"""
stats.py — Deck statistics and progress display.
"""

from datetime import date
from models import Deck
from scheduler import days_until_due

BOLD  = "\033[1m"
GREEN = "\033[92m"
CYAN  = "\033[96m"
YELLOW = "\033[93m"
RED   = "\033[91m"
RESET = "\033[0m"


def show_deck_stats(deck: Deck):
    total = len(deck.cards)
    if total == 0:
        print(f"\n  Deck is empty. Add some cards first!")
        return

    due_today = [c for c in deck.cards if c.is_due()]
    new_cards  = [c for c in deck.cards if c.repetitions == 0]
    learning   = [c for c in deck.cards if 0 < c.repetitions < 3]
    mature     = [c for c in deck.cards if c.repetitions >= 3]

    avg_ef = round(sum(c.easiness for c in deck.cards) / total, 2)

    print(f"\n{BOLD}{'═'*50}{RESET}")
    print(f"  {CYAN}{BOLD}{deck.name}{RESET}  ({deck.language})")
    print(f"{'─'*50}{RESET}")
    print(f"  Total cards    : {total}")
    print(f"  {RED}Due today      : {len(due_today)}{RESET}")
    print(f"  {YELLOW}New            : {len(new_cards)}{RESET}")
    print(f"  Learning       : {len(learning)}")
    print(f"  {GREEN}Mature         : {len(mature)}{RESET}")
    print(f"  Avg. easiness  : {avg_ef}")
    print(f"{'─'*50}{RESET}")

    # Upcoming schedule (next 7 days)
    print(f"\n  Upcoming reviews:")
    for offset in range(1, 8):
        target = date.today()
        from datetime import timedelta
        target_str = (date.today() + timedelta(days=offset)).isoformat()
        count = sum(1 for c in deck.cards if c.due_date == target_str)
        if count:
            label = "Tomorrow" if offset == 1 else f"In {offset} days"
            bar = "█" * min(count, 20)
            print(f"  {label:12} {count:3}  {GREEN}{bar}{RESET}")

    print(f"{BOLD}{'═'*50}{RESET}\n")


def list_all_cards(deck: Deck):
    if not deck.cards:
        print("\n  No cards in this deck.")
        return

    print(f"\n{BOLD}{'─'*65}{RESET}")
    print(f"  {'ID':8} {'FRONT':20} {'BACK':20} {'DUE':10} {'REPS':4}")
    print(f"{'─'*65}{RESET}")
    for c in sorted(deck.cards, key=lambda x: x.due_date):
        due_flag = f"{RED}TODAY{RESET}" if c.is_due() else c.due_date
        front = c.front[:18] + ".." if len(c.front) > 20 else c.front
        back  = c.back[:18]  + ".." if len(c.back)  > 20 else c.back
        print(f"  {c.card_id:8} {front:20} {back:20} {due_flag:10} {c.repetitions}")
    print(f"{BOLD}{'─'*65}{RESET}\n")
