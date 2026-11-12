"""
app.py — Flask Web UI for the Flashcard Engine
Run: python app.py
Visit: http://localhost:5000
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from models import Card, Deck
from storage import save_deck, load_deck, list_decks, delete_deck
from scheduler import rate_card
from stats import show_deck_stats  # used in API

app = Flask(__name__)


# ── helpers ──────────────────────────────────────────────────────────────

def deck_summary(deck: Deck) -> dict:
    due = deck.due_cards()
    new = deck.new_cards()
    mature = [c for c in deck.cards if c.repetitions >= 3]
    return {
        "name": deck.name,
        "language": deck.language,
        "description": deck.description,
        "total": len(deck.cards),
        "due": len(due),
        "new": len(new),
        "learning": len([c for c in deck.cards if 0 < c.repetitions < 3]),
        "mature": len(mature),
    }


def card_to_dict(card: Card) -> dict:
    return {
        "card_id": card.card_id,
        "front": card.front,
        "back": card.back,
        "transliteration": card.transliteration,
        "example": card.example,
        "repetitions": card.repetitions,
        "interval": card.interval,
        "easiness": card.easiness,
        "due_date": card.due_date,
        "is_due": card.is_due(),
    }


# ── pages ─────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    decks = list_decks()
    summaries = []
    for name in decks:
        try:
            deck = load_deck(name)
            summaries.append(deck_summary(deck))
        except Exception:
            pass
    return render_template("index.html", decks=summaries)


@app.route("/deck/<deck_name>")
def deck_view(deck_name):
    try:
        deck = load_deck(deck_name)
    except FileNotFoundError:
        return redirect(url_for("index"))
    summary = deck_summary(deck)
    cards = [card_to_dict(c) for c in deck.cards]
    return render_template("deck.html", summary=summary, cards=cards)


@app.route("/review/<deck_name>")
def review(deck_name):
    try:
        deck = load_deck(deck_name)
    except FileNotFoundError:
        return redirect(url_for("index"))
    cram = request.args.get("cram", "0") == "1"
    cap  = request.args.get("cap", "0")
    try:
        cap = int(cap)
    except ValueError:
        cap = 0
    if cram:
        due = deck.cards[:]
    else:
        due = deck.due_cards()
    if cap > 0:
        due = due[:cap]
    return render_template("review.html",
                           deck_name=deck.name,
                           language=deck.language,
                           due_count=len(due),
                           cram=cram,
                           cap=cap)


# ── API ──────────────────────────────────────────────────────────────────

@app.route("/api/decks", methods=["GET"])
def api_decks():
    decks = list_decks()
    summaries = []
    for name in decks:
        try:
            deck = load_deck(name)
            summaries.append(deck_summary(deck))
        except Exception:
            pass
    return jsonify(summaries)


@app.route("/api/decks", methods=["POST"])
def api_create_deck():
    data = request.json
    name = data.get("name", "").strip()
    language = data.get("language", "").strip()
    description = data.get("description", "").strip()
    if not name or not language:
        return jsonify({"error": "Name and language are required"}), 400
    deck = Deck(name=name, language=language, description=description)
    save_deck(deck)
    return jsonify(deck_summary(deck)), 201


@app.route("/api/decks/<deck_name>", methods=["DELETE"])
def api_delete_deck(deck_name):
    ok = delete_deck(deck_name)
    return jsonify({"deleted": ok})


@app.route("/api/decks/<deck_name>/cards", methods=["GET"])
def api_cards(deck_name):
    try:
        deck = load_deck(deck_name)
    except FileNotFoundError:
        return jsonify({"error": "Deck not found"}), 404
    return jsonify([card_to_dict(c) for c in deck.cards])


@app.route("/api/decks/<deck_name>/cards", methods=["POST"])
def api_add_card(deck_name):
    try:
        deck = load_deck(deck_name)
    except FileNotFoundError:
        return jsonify({"error": "Deck not found"}), 404
    data = request.json
    front = data.get("front", "").strip()
    back = data.get("back", "").strip()
    if not front or not back:
        return jsonify({"error": "front and back are required"}), 400
    card = Card(
        front=front,
        back=back,
        transliteration=data.get("transliteration", "").strip(),
        example=data.get("example", "").strip(),
    )
    deck.add_card(card)
    save_deck(deck)
    return jsonify(card_to_dict(card)), 201


@app.route("/api/decks/<deck_name>/cards/<card_id>", methods=["DELETE"])
def api_delete_card(deck_name, card_id):
    try:
        deck = load_deck(deck_name)
    except FileNotFoundError:
        return jsonify({"error": "Deck not found"}), 404
    ok = deck.remove_card(card_id)
    if ok:
        save_deck(deck)
    return jsonify({"deleted": ok})


@app.route("/api/review/<deck_name>/next", methods=["GET"])
def api_review_next(deck_name):
    """Return the next due card for review."""
    try:
        deck = load_deck(deck_name)
    except FileNotFoundError:
        return jsonify({"error": "Deck not found"}), 404
    cram = request.args.get("cram", "0") == "1"
    import random
    if cram:
        pool = deck.cards[:]
        random.shuffle(pool)
        card = pool[0] if pool else None
        remaining = len(pool)
    else:
        due = deck.due_cards()
        if not due:
            return jsonify({"done": True, "remaining": 0})
        card = random.choice(due)
        remaining = len(due)
    if not card:
        return jsonify({"done": True, "remaining": 0})
    return jsonify({
        "done": False,
        "remaining": remaining,
        "card": card_to_dict(card),
    })


@app.route("/api/review/<deck_name>/rate", methods=["POST"])
def api_review_rate(deck_name):
    """Submit a rating for a card."""
    try:
        deck = load_deck(deck_name)
    except FileNotFoundError:
        return jsonify({"error": "Deck not found"}), 404
    data = request.json
    card_id = data.get("card_id")
    rating = data.get("rating")
    if rating is None or not (0 <= int(rating) <= 5):
        return jsonify({"error": "Rating must be 0-5"}), 400
    card = deck.get_card(card_id)
    if not card:
        return jsonify({"error": "Card not found"}), 404
    rate_card(card, int(rating))
    save_deck(deck)
    return jsonify({
        "card": card_to_dict(card),
        "remaining": len(deck.due_cards()),
    })


if __name__ == "__main__":
    print("\n  🃏 Flashcard Engine — Web UI")
    print("  Visit: http://localhost:5000\n")
    app.run(debug=True, port=5000)
