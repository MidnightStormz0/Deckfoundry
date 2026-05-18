from django.contrib import admin
from .models import Card


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ("name", "type_line", "mana_cost", "commander_legal")
    search_fields = ("name", "type_line", "oracle_text")
    list_filter = ("commander_legal",)