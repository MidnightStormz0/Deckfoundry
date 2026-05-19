from django import forms
from .models import Deck


class DeckForm(forms.ModelForm):
    selected_cards_data = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Deck
        fields = ["name", "description", "archetype", "selected_cards_data"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Deck name"}),
            "description": forms.Textarea(attrs={"rows": 4, "placeholder": "Describe the deck"}),
            "archetype": forms.TextInput(attrs={"placeholder": "Example: +1/+1 counters, Reanimator, Control"}),
        }
        labels = {
            "name": "Deck name",
            "description": "Description",
            "archetype": "Archetype",
        }
