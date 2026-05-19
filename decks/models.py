from django.db import models
from django.utils import timezone


class Deck(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    archetype = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "name"]

    def __str__(self):
        return self.name

    @property
    def total_cards(self):
        return sum(item.quantity for item in self.cards.select_related('card').all())


class DeckCard(models.Model):
    deck = models.ForeignKey(Deck, related_name="cards", on_delete=models.CASCADE)
    card = models.ForeignKey("cards.Card", on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    role = models.CharField(max_length=100, blank=True)

    class Meta:
        unique_together = ("deck", "card")
        ordering = ["card__name"]

    def __str__(self):
        return f"{self.quantity}× {self.card.name}"
