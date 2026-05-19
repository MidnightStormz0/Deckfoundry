from django.contrib import admin

from .models import Deck, DeckCard


@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    list_display = ("name", "archetype", "updated_at")
    search_fields = ("name", "archetype")


@admin.register(DeckCard)
class DeckCardAdmin(admin.ModelAdmin):
    list_display = ("deck", "card", "quantity", "role")
    list_filter = ("deck",)
