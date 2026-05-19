# Changelog

All notable changes to this project are recorded in this file.

## [Unreleased]

### Added
- New `decks` Django app providing deck creation, editing, and dashboard analytics.
  - Models: `Deck`, `DeckCard` (deck/models.py)
  - Views: deck list, create, edit, detail, and a JSON card search endpoint (decks/views.py)
  - Templates: `decks/templates/decks/deck_list.html`, `deck_form.html`, `deck_detail.html`
  - Forms: `decks/forms.py` (DeckForm)
  - Static: `static/js/deck_picker.js` (live card picker), CSS updates in `static/css/styles.css`
  - Admin registration for `Deck` and `DeckCard` (decks/admin.py)

### UX
- Deck builder includes a live card search and a client-side picker for adding/removing cards.
- Deck browser shows card-art previews and a responsive grid on the decks homepage.

### Notes
- Decks are currently global (no per-user ownership) — consider adding authentication for user-specific deck storage.

---

Generated on: 2026-05-18
