from django.shortcuts import render

from .services.prompt_analyzer import analyze_prompt
from .services.card_recommender import find_cards_for_terms, find_commanders_for_analysis


def home(request):
    prompt = ''
    analysis = None
    results = {}
    commanders = []

    if request.method == 'POST':
        prompt = request.POST.get('prompt', '').strip()
        if prompt:
            # Keep analyzer swappable: analyze_prompt is the entrypoint
            analysis = analyze_prompt(prompt)
            results = find_cards_for_terms(analysis.get('search_terms', []))
            # Provide commander suggestions for matching archetypes
            commanders = find_commanders_for_analysis(analysis)

    context = {
        'prompt': prompt,
        'analysis': analysis or {
            'themes': [],
            'colors': [],
            'budget': None,
            'power_level': None,
            'search_terms': [],
        },
        'results': results,
        'commanders': commanders,
    }

    return render(request, 'ai_builder/home.html', context)
