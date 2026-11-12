"""
main.py — Local Language Flashcard Engine (CLI)

Usage:
    python main.py

A spaced-repetition flashcard tool for learning local/regional languages.
Uses the SM-2 algorithm (same as Anki) to schedule cards based on your recall.
"""

import sys
from models import Card, Deck
from storage import save_deck, load_deck, list_decks, delete_deck
from session import run_session
from stats import show_deck_stats, list_all_cards

# ANSI colours
BOLD   = "\033[1m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
RESET  = "\033[0m"

BANNER = f"""
{CYAN}{BOLD}
 ██████╗  █████╗ ██████╗ ██████╗ ███████╗
██╔════╝ ██╔══██╗██╔══██╗██╔══██╗██╔════╝
██║      ███████║██████╔╝██║  ██║███████╗
██║      ██╔══██║██╔══██╗██║  ██║╚════██║
╚██████╗ ██║  ██║██║  ██║██████╔╝███████║
 ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚══════╝
{RESET}{BOLD} Local Language Flashcard Engine  •  SM-2 Spaced Repetition{RESET}
"""


# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────

def hr(char="─", width=50):
    print(f"{BOLD}{char * width}{RESET}")


def prompt(text: str, default: str = "") -> str:
    val = input(f"  {text}: ").strip()
    return val if val else default


def choose(options: list[str], label="Choose") -> int:
    for i, opt in enumerate(options, 1):
        print(f"    {BOLD}{i}.{RESET} {opt}")
    while True:
        try:
            n = int(input(f"\n  {label} (1-{len(options)}): ").strip())
            if 1 <= n <= len(options):
                return n - 1
        except (ValueError, EOFError):
            pass
        print(f"  {RED}Invalid choice.{RESET}")


# ─────────────────────────────────────────────
#  Deck management
# ─────────────────────────────────────────────

def select_deck() -> Deck | None:
    decks = list_decks()
    if not decks:
        print(f"\n  {YELLOW}No decks found. Create one first!{RESET}")
        return None
    print(f"\n{BOLD}  Available decks:{RESET}")
    idx = choose(decks, "Select deck")
    return load_deck(decks[idx])


def create_deck():
    print(f"\n{BOLD}  Create New Deck{RESET}")
    hr()
    name     = prompt("Deck name (e.g. 'Hindi Basics')")
    language = prompt("Language (e.g. 'Hindi', 'Punjabi', 'Tamil')")
    desc     = prompt("Description (optional)")

    if not name or not language:
        print(f"  {RED}Name and language are required.{RESET}")
        return

    deck = Deck(name=name, language=language, description=desc)
    save_deck(deck)
    print(f"\n  {GREEN}✓ Deck '{name}' created!{RESET}")


# ─────────────────────────────────────────────
#  Card management
# ─────────────────────────────────────────────

def add_card(deck: Deck):
    print(f"\n{BOLD}  Add Card to '{deck.name}'{RESET}")
    hr()
    print(f"  {YELLOW}Tip: Paste the local language word/phrase as the front.{RESET}\n")

    while True:
        front  = prompt("Front (local language word/phrase)")
        back   = prompt("Back (translation / meaning)")
        transl = prompt("Transliteration / pronunciation (optional)")
        ex     = prompt("Example sentence (optional)")

        if not front or not back:
            print(f"  {RED}Front and back are required.{RESET}")
        else:
            card = Card(front=front, back=back,
                        transliteration=transl, example=ex)
            deck.add_card(card)
            save_deck(deck)
            print(f"\n  {GREEN}✓ Card added! (ID: {card.card_id}){RESET}")

        again = input("\n  Add another card? (y/n): ").strip().lower()
        if again != "y":
            break


def remove_card(deck: Deck):
    list_all_cards(deck)
    if not deck.cards:
        return
    card_id = prompt("Enter card ID to remove (or blank to cancel)")
    if not card_id:
        return
    if deck.remove_card(card_id):
        save_deck(deck)
        print(f"  {GREEN}✓ Card removed.{RESET}")
    else:
        print(f"  {RED}Card ID not found.{RESET}")


def bulk_add_cards(deck: Deck):
    """Add multiple cards from a simple text format."""
    print(f"\n{BOLD}  Bulk Add Cards{RESET}")
    hr()
    print(f"  Enter one card per line in this format:")
    print(f"  {CYAN}front | back | transliteration(opt) | example(opt){RESET}")
    print(f"  Type a blank line when done.\n")

    added = 0
    while True:
        line = input("  > ").strip()
        if not line:
            break
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 2:
            print(f"  {RED}Need at least front | back{RESET}")
            continue
        front, back = parts[0], parts[1]
        transl = parts[2] if len(parts) > 2 else ""
        ex     = parts[3] if len(parts) > 3 else ""
        deck.add_card(Card(front=front, back=back, transliteration=transl, example=ex))
        added += 1

    if added:
        save_deck(deck)
        print(f"\n  {GREEN}✓ {added} card(s) added!{RESET}")


# ─────────────────────────────────────────────
#  Deck menu
# ─────────────────────────────────────────────

def deck_menu(deck: Deck):
    due_count = len(deck.due_cards())

    while True:
        print(f"\n{BOLD}  ── {deck.name} ({deck.language}) ──{RESET}")
        due_label = f"{RED}{due_count} due{RESET}" if due_count else f"{GREEN}0 due{RESET}"
        print(f"  {len(deck.cards)} cards total  •  {due_label}")
        hr("─")

        options = [
            f"{'🔔 ' if due_count else ''}Start Review Session",
            "Add Card",
            "Bulk Add Cards",
            "Remove Card",
            "View All Cards",
            "Deck Statistics",
            "← Back",
        ]
        idx = choose(options)

        if idx == 0:
            run_session(deck)
            due_count = len(deck.due_cards())   # refresh
        elif idx == 1:
            add_card(deck)
        elif idx == 2:
            bulk_add_cards(deck)
        elif idx == 3:
            remove_card(deck)
        elif idx == 4:
            list_all_cards(deck)
        elif idx == 5:
            show_deck_stats(deck)
        elif idx == 6:
            break


# ─────────────────────────────────────────────
#  Main menu
# ─────────────────────────────────────────────

def main_menu():
    print(BANNER)

    while True:
        hr("═")
        print(f"{BOLD}  MAIN MENU{RESET}")
        hr("─")

        decks = list_decks()
        if decks:
            total_due = sum(
                len(load_deck(d).due_cards()) for d in decks
            )
            summary = f"{len(decks)} deck(s)"
            if total_due:
                summary += f"  •  {RED}{BOLD}{total_due} card(s) due today{RESET}"
            print(f"  {summary}\n")

        options = [
            "Open a Deck",
            "Create New Deck",
            "Delete a Deck",
            "Quit",
        ]
        idx = choose(options)

        if idx == 0:
            deck = select_deck()
            if deck:
                deck_menu(deck)
        elif idx == 1:
            create_deck()
        elif idx == 2:
            deck = select_deck()
            if deck:
                confirm = input(
                    f"\n  Delete '{deck.name}'? This is permanent. (yes/no): "
                ).strip().lower()
                if confirm == "yes":
                    delete_deck(deck.name)
                    print(f"  {RED}Deck deleted.{RESET}")
        elif idx == 3:
            print(f"\n  {CYAN}Good luck with your studies! 🎉{RESET}\n")
            sys.exit(0)


# ─────────────────────────────────────────────

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n  {YELLOW}Interrupted. Bye!{RESET}\n")
