# 🃏 Local Language Flashcard Engine

A terminal-based spaced repetition flashcard app for learning local/regional languages.  
Uses the **SM-2 algorithm** (same algorithm as Anki) to schedule card reviews intelligently.

---

## Features

- **SM-2 spaced repetition** — cards you know well appear less often, hard cards come back sooner
- **Any language pair** — Hindi ↔ English, Punjabi ↔ English, Tamil ↔ English, etc.
- **Unicode support** — works with Devanagari, Gurmukhi, Tamil script, and more
- **Transliteration + examples** — store pronunciation hints and example sentences
- **Bulk card import** — add many cards at once with a simple pipe-separated format
- **Session stats** — accuracy bar, correct/total counts, upcoming review schedule
- **Pure Python** — no external dependencies, data stored as readable JSON

---

## Setup

```bash
# No pip install needed — standard library only
python main.py
```

Requires **Python 3.10+** (for the `list[str]` type hints).

---

## Project Structure

```
flashcard_engine/
├── main.py        # CLI entry point and menus
├── models.py      # Card and Deck dataclasses
├── scheduler.py   # SM-2 algorithm
├── session.py     # Review session logic
├── storage.py     # JSON save/load
├── stats.py       # Statistics display
└── data/
    └── hindi_basics.json   # Sample deck
```

---

## SM-2 Rating Scale

| Rating | Meaning                        |
|--------|--------------------------------|
| 0      | Complete blackout              |
| 1      | Wrong — answer felt familiar   |
| 2      | Wrong — but easy once seen     |
| 3      | Correct with significant effort|
| 4      | Correct after a hesitation     |
| 5      | Perfect, instant recall        |

Cards rated **0–2** are reset and reviewed again in the same session.  
Cards rated **3–5** are scheduled for a future date.

---

## Bulk Add Format

```
नमस्ते | Hello | Namaste | नमस्ते! आप कैसे हैं?
पानी | Water | Paani | मुझे पानी चाहिए।
```

Format: `front | back | transliteration(optional) | example(optional)`

---

## Possible Extensions

- [ ] CSV/TSV import from Google Sheets
- [ ] Multiple choice quiz mode
- [ ] Web UI with Flask or FastAPI
- [ ] Audio playback with `gTTS`
- [ ] Export progress report as PDF
- [ ] Deck sharing (JSON export/import)
