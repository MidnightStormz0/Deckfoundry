from django.urls import path
from . import views

app_name = "cards"

urlpatterns = [
    path("", views.card_list, name="card_list"),
    path("<uuid:oracle_id>/", views.card_detail, name="card_detail"),
]