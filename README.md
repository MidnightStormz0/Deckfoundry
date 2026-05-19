# Deckfoundry

A natural-language based magic the gathering commander deck builder. Describe any type of magic deck you want it automatically receive curated suggestions to turn into a deck.

## Releases

See `CHANGELOG.md` for release history. The first release `v0.1.0` adds a `decks` app with deck creation, editing, a live card picker, and a dashboard. Database migrations for the `decks` app are included in `decks/migrations/0001_initial.py`.

### Release workflow

- Add feature code and update `CHANGELOG.md` with a new release section or entry.
- Commit feature changes with a descriptive message.
- Create a tag for the release, for example `git tag -a v0.1.1 -m 'v0.1.1: initial AI deck prompt analyzer feature'`.
- Push the branch and tag to GitHub: `git push origin main && git push origin v0.1.1`.
