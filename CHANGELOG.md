# Changelog

All notable changes to this project are recorded in this file.

## [v0.1.0] - 2026-05-18

### Added

- New `decks` Django app providing deck creation, editing, and dashboard analytics.
  - Models: `Deck`, `DeckCard` (`decks/models.py`)
  - Views: deck list, create, edit, detail, and a JSON card search endpoint (`decks/views.py`)
  - Templates: `decks/templates/decks/deck_list.html`, `deck_form.html`, `deck_detail.html`
  - Forms: `decks/forms.py` (`DeckForm`)
  - Static: `static/js/deck_picker.js` (live card picker), CSS updates in `static/css/styles.css`
  - Admin registration for `Deck` and `DeckCard` (`decks/admin.py`)

### Migrations

- Database migration for the `decks` app: `decks/migrations/0001_initial.py` (creates `Deck` and `DeckCard` tables). Run `python manage.py migrate` to apply.

### UX

- Deck builder includes a live card search and a client-side picker for adding/removing cards.
- Deck browser shows card-art previews and a responsive grid on the decks homepage.

### Notes

- Decks are currently global (no per-user ownership) — consider adding authentication for user-specific deck storage.

---

Unreleased changes can be added under `## [Unreleased]`.
