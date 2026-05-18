from django.db.models import Case, IntegerField, Q, Value, When
from django.shortcuts import render, get_object_or_404

from .models import Card



def card_detail(request, oracle_id):
    printings = Card.objects.filter(
        oracle_id=oracle_id
    ).order_by("-released_at", "set_code")

    card = printings.filter(image_url__isnull=False).exclude(image_url="").first()

    if card is None:
        card = printings.first()

    return render(
        request,
        "cards/card_detail.html",
        {
            "card": card,
            "printings": printings,
        },
    )

def unique_by_oracle_id(cards):
    unique_cards = {}

    for card in cards:
        key = card.oracle_id or card.scryfall_id

        if key not in unique_cards:
            unique_cards[key] = card

    return list(unique_cards.values())


def card_list(request):
    query = request.GET.get("q", "").strip()

    cards = []
    search_mode = None

    if query:
        word_name_match = (
            Q(name__iexact=query)
            | Q(name__istartswith=f"{query} ")
            | Q(name__icontains=f" {query} ")
            | Q(name__iendswith=f" {query}")
        )

        name_matches = (
            Card.objects.filter(
                word_name_match,
                oracle_id__isnull=False,)
            .annotate(
                search_rank=Case(
                    When(name__iexact=query, then=Value(0)),
                    When(name__istartswith=f"{query} ", then=Value(1)),
                    When(name__icontains=f" {query} ", then=Value(2)),
                    When(name__iendswith=f" {query}", then=Value(3)),
                    default=Value(4),
                    output_field=IntegerField(),
                )
            )
            .order_by("search_rank", "name")
        )

        if name_matches.exists():
            cards = unique_by_oracle_id(name_matches[:500])[:100]
            search_mode = "name"
        else:
            text_matches = (
                Card.objects.filter(
                    Q(type_line__icontains=query)
                    | Q(oracle_text__icontains=query),
                    oracle_id__isnull=False,
                )
                .order_by("name")[:100]
            )

            cards = unique_by_oracle_id(text_matches[:500])[:100]
            search_mode = "type_or_oracle"

    return render(
        request,
        "cards/card_list.html",
        {
            "cards": cards,
            "query": query,
            "search_mode": search_mode,
        },
    )