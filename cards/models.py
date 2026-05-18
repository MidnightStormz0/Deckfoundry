from django.db import models


class Card(models.Model):
    scryfall_id = models.UUIDField(unique=True, default=None, null=True, blank=True)
    oracle_id = models.UUIDField(null=True, blank=True)

    name = models.CharField(max_length=255)
    mana_cost = models.CharField(max_length=100, blank=True)
    cmc = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    type_line = models.CharField(max_length=255, blank=True)
    oracle_text = models.TextField(blank=True)

    colors = models.JSONField(default=list, blank=True)
    color_identity = models.JSONField(default=list, blank=True)

    legalities = models.JSONField(default=dict, blank=True)
    commander_legal = models.BooleanField(default=False)

    image_url = models.URLField(blank=True, default="")
    scryfall_uri = models.URLField(blank=True)

    released_at = models.DateField(null=True, blank=True)
    set_code = models.CharField(max_length=20, blank=True)
    rarity = models.CharField(max_length=50, blank=True)

    prices = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name