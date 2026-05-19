import re
from collections import OrderedDict

# Rules for simple, rule-based prompt analysis. Each theme includes
# a list of keywords to match in the user's prompt and one or more
# search phrases that will be used to find matching cards locally.
THEME_RULES = {
    'graveyard': {
        'keywords': ['graveyard', 'reanimat', 'reanimate', 'dredge', 'mill', 'grave'],
        'search_terms': ['graveyard', 'reanimate', 'return from graveyard', 'dredge', 'mill']
    },
    'theft': {
        'keywords': ['steal', 'stealing', 'steals', 'steal creatures', 'thief', 'take control'],
        'search_terms': ['gain control', 'steal', 'gain control of target']
    },
    'lifegain': {
        'keywords': ['lifegain', 'life gain', 'lifelink', 'gain life'],
        'search_terms': ['lifegain', 'lifelink', 'gain life']
    },
    'tokens': {
        'keywords': ['tokens', 'token', 'create tokens', 'token token'],
        'search_terms': ['create token', 'token', 'populate']
    },
    'counters': {
        'keywords': ['+1/+1', 'counters', 'counters matter', 'counter'],
        'search_terms': ['+1/+1 counters', 'counters']
    },
    'artifacts': {
        'keywords': ['artifact', 'artifacts', 'equipment'],
        'search_terms': ['artifact', 'equipment']
    },
    'spellslinger': {
        'keywords': ['spellslinger', 'spells', 'spell slinger'],
        'search_terms': ['spells', 'instant', 'sorcery']
    },
    'aristocrats': {
        'keywords': ['aristocrat', 'aristocrats', 'sacrifice', 'sacrifice deck'],
        'search_terms': ['sacrifice', 'death trigger', 'when .* dies']
    },
    'vampires': {
        'keywords': ['vampire', 'vampires'],
        'search_terms': ['vampire']
    },
    'dragons': {
        'keywords': ['dragon', 'dragons'],
        'search_terms': ['dragon']
    },
    'equipment': {
        'keywords': ['equipment', 'equip'],
        'search_terms': ['equipment', 'equip']
    },
    'enchantments': {
        'keywords': ['enchantment', 'enchantments', 'aura'],
        'search_terms': ['enchantment', 'aura']
    },
    'blink': {
        'keywords': ['blink', 'flicker', 'exile then return', 'enter the battlefield'],
        'search_terms': ['blink', 'exile', 'enter the battlefield']
    },
    'mill': {
        'keywords': ['mill', 'milling', 'mill deck'],
        'search_terms': ['mill', 'put the top']
    },
    'reanimation': {
        'keywords': ['reanimation', 'reanimate', 'reanimator'],
        'search_terms': ['reanimate', 'return from graveyard']
    },
    'sacrifice': {
        'keywords': ['sacrifice', 'sacrifices'],
        'search_terms': ['sacrifice']
    }
}

# Simple color words and guild names mapping to colors
COLOR_MAP = {
    'white': ['white'],
    'blue': ['blue'],
    'black': ['black'],
    'red': ['red'],
    'green': ['green'],
    'azorius': ['white', 'blue'],
    'dimir': ['blue', 'black'],
    'rakdos': ['black', 'red'],
    'gruul': ['red', 'green'],
    'selesnya': ['white', 'green'],
    'orzhov': ['white', 'black'],
    'izzet': ['blue', 'red'],
    'golgari': ['green', 'black'],
    'boros': ['red', 'white'],
    'simic': ['green', 'blue'],
    'esper': ['white', 'blue', 'black'],
    'grixis': ['blue', 'black', 'red'],
    'jund': ['black', 'red', 'green'],
    'naya': ['red', 'green', 'white'],
    'bant': ['green', 'white', 'blue'],
    'mardu': ['red', 'white', 'black'],
    'temur': ['blue', 'green', 'red'],
    'abzan': ['white', 'black', 'green'],
    'sultai': ['black', 'green', 'blue'],
    'jeskai': ['white', 'blue', 'red'],
    'five color': ['white', 'blue', 'black', 'red', 'green'],
    'colorless': ['colorless'],
}

STOP_WORDS = set(['i', 'want', 'a', 'the', 'with', 'and', 'to', 'that', 'of', 'in', 'for', 'my', 'on', 'is', 'it', 'its'])


def _dedupe_preserve_order(items):
    seen = set()
    out = []
    for it in items:
        if it in seen:
            continue
        seen.add(it)
        out.append(it)
    return out


def rule_based_analyze_prompt(prompt):
    text = prompt.lower()

    detected_themes = []
    detected_search_terms = []

    # detect themes
    for theme, info in THEME_RULES.items():
        for kw in info.get('keywords', []):
            if kw in text:
                detected_themes.append(theme)
                detected_search_terms.extend(info.get('search_terms', []))
                break

    # detect colors
    detected_colors = []
    for name, cols in COLOR_MAP.items():
        if name in text:
            for c in cols:
                detected_colors.append(c)

    # budget detection
    budget = None
    if re.search(r'\b(no budget|no-budget)\b', text):
        budget = 'no_budget'
    elif re.search(r'\b(budget|cheap|affordable|cheaper)\b', text):
        budget = 'budget'
    elif re.search(r'\b(expensive|high end|premium)\b', text):
        budget = 'expensive'

    # power level detection
    power_level = None
    if re.search(r'\b(cedh|c?edh)\b', text):
        power_level = 'cEDH'
    elif 'competitive' in text or 'high power' in text or 'high-power' in text:
        power_level = 'competitive'
    elif 'precon' in text:
        power_level = 'precon'
    elif 'casual' in text:
        power_level = 'casual'

    # extract additional search terms from prompt words (simple heuristic)
    words = re.findall(r"[a-zA-Z0-9\+\#\'\-]+", text)
    extra_terms = []
    for w in words:
        if w in STOP_WORDS:
            continue
        # ignore single-letter tokens
        if len(w) <= 2:
            continue
        # avoid adding words that are already theme keywords or colours
        if any(w in ' '.join(info['keywords']) for info in THEME_RULES.values()):
            continue
        extra_terms.append(w)

    # Build search_terms: theme phrases, colors, and a few extra words
    final_search_terms = []
    final_search_terms.extend(detected_search_terms)
    final_search_terms.extend(detected_colors)
    # take up to 6 extra terms to keep queries reasonable
    final_search_terms.extend(extra_terms[:6])

    final_search_terms = _dedupe_preserve_order(final_search_terms)
    detected_themes = _dedupe_preserve_order(detected_themes)
    detected_colors = _dedupe_preserve_order(detected_colors)

    return {
        'themes': detected_themes,
        'colors': detected_colors,
        'budget': budget,
        'power_level': power_level,
        'search_terms': final_search_terms,
    }


def analyze_prompt(prompt):
    """Main analyzer entrypoint.

    This function exists so we can swap implementations later. For now it
    delegates to the rule-based analyzer, but it could be changed to call
    an AI-powered analyzer without touching the views.
    """
    return rule_based_analyze_prompt(prompt)
