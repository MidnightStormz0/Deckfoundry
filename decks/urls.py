from django.urls import path
from . import views

app_name = "decks"

urlpatterns = [
    path("", views.deck_list, name="deck_list"),
    path("create/", views.deck_create, name="deck_create"),
    path("<int:deck_id>/", views.deck_detail, name="deck_detail"),
    path("<int:deck_id>/edit/", views.deck_edit, name="deck_edit"),
    path("cards/search/", views.card_search_json, name="card_search_json"),
]
