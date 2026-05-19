from django.db.models import Q

from cards.models import Card


def unique_by_oracle_id(cards):
    seen = set()
    out = []
    for c in cards:
        oid = getattr(c, 'oracle_id', None)
        if not oid:
            continue
        if oid in seen:
            continue
        seen.add(oid)
        out.append(c)
    return out


def _matches_color_identity(card, requested_colors):
    if not requested_colors:
        return True

    requested_colors = set(requested_colors)
    card_colors = set(getattr(card, 'color_identity', []) or [])

    if requested_colors == {'colorless'}:
        return not card_colors

    if not card_colors:
        return False

    return card_colors.issubset(requested_colors) and bool(card_colors & requested_colors)


def find_cards_for_terms(terms, per_term=8):
    """Find cards matching each search term.

    - Only returns cards with `commander_legal=True` and non-null `oracle_id`.
    - Searches `name`, `type_line`, and `oracle_text` using case-insensitive contains.
    - Groups results by `oracle_id` to avoid duplicate printings.
    """
    results = {}

    for term in terms:
        if not term:
            continue
        qs = (
            Card.objects.filter(commander_legal=True)
            .exclude(oracle_id__isnull=True)
            .filter(
                Q(name__icontains=term) | Q(type_line__icontains=term) | Q(oracle_text__icontains=term)
            )
            .order_by('name')
        )

        # Fetch more rows before de-duplicating to get enough unique cards
        fetched = list(qs[: per_term * 3])
        unique = unique_by_oracle_id(fetched)
        results[term] = unique[:per_term]

    return results


def find_commanders_for_analysis(analysis, limit=6):
    """Return a short list of commander candidates that match the analysis.

    Currently focuses on matching Legendary Creature commanders that mention
    theme-related terms (e.g., graveyard keywords). This is a heuristic to
    suggest commanders that fit the archetype.
    """
    # Lazy import of theme rules to avoid circular imports
    try:
        from ai_builder.services.prompt_analyzer import THEME_RULES
    except Exception:
        THEME_RULES = {}

    terms = []
    # If a theme is present and has search_terms, gather them
    for theme in analysis.get('themes', []):
        info = THEME_RULES.get(theme, {})
        terms.extend(info.get('search_terms', []))

    # Also include generic search terms from the analysis
    terms.extend(analysis.get('search_terms', []))

    # dedupe while preserving order
    seen = set()
    dedup_terms = []
    for t in terms:
        if not t:
            continue
        if t in seen:
            continue
        seen.add(t)
        dedup_terms.append(t)

    if not dedup_terms:
        return []

    requested_colors = analysis.get('colors', [])
    requested_colors = [c for c in requested_colors if c]

    # Build a combined Q for all terms
    q_all = Q()
    for term in dedup_terms:
        q_all |= Q(name__icontains=term) | Q(type_line__icontains=term) | Q(oracle_text__icontains=term)

    qs = (
        Card.objects.filter(commander_legal=True)
        .exclude(oracle_id__isnull=True)
        .filter(type_line__icontains='Legendary')
        .filter(type_line__icontains='Creature')
        .filter(q_all)
        .order_by('name')
    )

    fetched = list(qs[: limit * 4])
    unique = unique_by_oracle_id(fetched)

    if requested_colors:
        unique = [card for card in unique if _matches_color_identity(card, requested_colors)]

    return unique[:limit]
