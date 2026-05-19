import json

from collections import Counter
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from cards.models import Card
from .forms import DeckForm
from .models import Deck, DeckCard


def unique_by_oracle_id(cards):
    unique = {}

    for card in cards:
        key = card.oracle_id or card.scryfall_id or card.id
        existing = unique.get(key)
        if existing is None:
            unique[key] = card
        elif not existing.image_url and card.image_url:
            unique[key] = card

    return list(unique.values())


def parse_selected_cards_json(data):
    if not data:
        return []
    try:
        items = json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return []

    selected = []
    seen = {}
    for item in items:
        card_id = item.get("card_id")
        quantity = item.get("quantity", 1)
        if card_id is None:
            continue
        try:
            quantity = max(1, int(quantity))
        except (TypeError, ValueError):
            quantity = 1

        if card_id in seen:
            seen[card_id] += quantity
        else:
            seen[card_id] = quantity

    for card_id, quantity in seen.items():
        selected.append({"card_id": card_id, "quantity": quantity})

    return selected


def card_search_json(request):
    query = request.GET.get("q", "").strip()
    if not query:
        return JsonResponse({"results": []})

    matches = list(
        Card.objects.filter(
            Q(name__icontains=query)
            | Q(type_line__icontains=query)
            | Q(oracle_text__icontains=query),
            oracle_id__isnull=False,
        )
        .order_by("name")[:200]
    )

    search_cards = unique_by_oracle_id(matches)[:30]
    results = [
        {
            "card_id": card.id,
            "name": card.name,
            "type_line": card.type_line,
            "mana_cost": card.mana_cost,
            "oracle_text": card.oracle_text,
            "oracle_id": str(card.oracle_id) if card.oracle_id else None,
            "image_url": card.image_url,
        }
        for card in search_cards
    ]

    return JsonResponse({"results": results})


def build_color_label(colors):
    if not colors:
        return "Colorless"
    return "+".join(sorted(colors))


def deck_list(request):
    decks = Deck.objects.prefetch_related("cards__card").all()
    deck_count = decks.count()
    total_deck_cards = sum(deck.total_cards for deck in decks)

    archetype_counter = Counter()
    color_counter = Counter()

    for deck in decks:
        archetype_counter[deck.archetype or "Unspecified"] += 1
        deck_colors = set()
        for item in deck.cards.all():
            deck_colors.update(item.card.color_identity or [])
        color_counter[build_color_label(deck_colors)] += 1

    archetype_chart = [
        {"label": label, "count": count, "pct": int(count / deck_count * 100)}
        for label, count in archetype_counter.most_common()
    ]
    color_chart = [
        {"label": label, "count": count, "pct": int(count / deck_count * 100)}
        for label, count in color_counter.most_common()
    ]

    return render(
        request,
        "decks/deck_list.html",
        {
            "decks": decks,
            "deck_count": deck_count,
            "total_deck_cards": total_deck_cards,
            "archetype_chart": archetype_chart,
            "color_chart": color_chart,
        },
    )


def get_initial_selected_cards(deck):
    items = []
    for item in deck.cards.select_related("card").all():
        items.append(
            {
                "card_id": item.card_id,
                "quantity": item.quantity,
                "name": item.card.name,
                "type_line": item.card.type_line,
            }
        )
    return items


def save_deck_cards(deck, raw_data):
    selected_items = parse_selected_cards_json(raw_data)
    deck.cards.all().delete()

    cards_to_create = []
    card_ids = [item["card_id"] for item in selected_items]
    cards = {card.id: card for card in Card.objects.filter(id__in=card_ids)}

    for entry in selected_items:
        card = cards.get(entry["card_id"])
        if card is None:
            continue
        cards_to_create.append(
            DeckCard(deck=deck, card=card, quantity=entry["quantity"])
        )

    DeckCard.objects.bulk_create(cards_to_create)


def deck_create(request):
    form = DeckForm(request.POST or None)
    selected_cards = []

    if request.method == "POST" and form.is_valid():
        deck = form.save(commit=False)
        deck.save()
        save_deck_cards(deck, form.cleaned_data.get("selected_cards_data", ""))
        return redirect("decks:deck_detail", deck_id=deck.id)

    return render(
        request,
        "decks/deck_form.html",
        {
            "form": form,
            "deck": None,
            "selected_cards": json.dumps(selected_cards),
        },
    )


def deck_edit(request, deck_id):
    deck = get_object_or_404(Deck, pk=deck_id)
    form = DeckForm(request.POST or None, instance=deck)
    selected_cards = get_initial_selected_cards(deck)

    if request.method == "POST" and form.is_valid():
        deck = form.save(commit=False)
        deck.save()
        save_deck_cards(deck, form.cleaned_data.get("selected_cards_data", ""))
        return redirect("decks:deck_detail", deck_id=deck.id)

    return render(
        request,
        "decks/deck_form.html",
        {
            "form": form,
            "deck": deck,
            "selected_cards": json.dumps(selected_cards),
        },
    )


def deck_detail(request, deck_id):
    deck = get_object_or_404(Deck, pk=deck_id)
    cards = deck.cards.select_related("card").all()
    return render(
        request,
        "decks/deck_detail.html",
        {
            "deck": deck,
            "cards": cards,
        },
    )
