from flask import request, session, g

try:
    from flask_babel import gettext, Babel
except Exception:
    # Fallback when Flask-Babel is not installed in the environment
    def gettext(msg):
        return msg
    
    class Babel:  # type: ignore
        def localeselector(self, fn):
            return fn

# Langues supportées (pour sélection dans l'interface)
LANGUAGES = {
    'fr': 'Français',
    'en': 'English',
    'ar': 'العربية',
}

def get_lang():
    """Detect the current language from g, session, cookies, or Accept-Language header.

    Priority:
    1. `g.lang` (set by before_request)
    2. `session['lang']`
    3. `lang` cookie
    4. `Accept-Language` header
    5. fallback 'fr'
    """
    # 1) g.lang (set in before_request)
    lang = getattr(g, 'lang', None)
    if lang in LANGUAGES:
        return lang

    # 2) session
    lang = session.get('lang')
    if lang in LANGUAGES:
        return lang

    # 3) cookie
    lang = request.cookies.get('lang')
    if lang in LANGUAGES:
        session['lang'] = lang
        return lang

    # 4) Accept-Language
    best = request.accept_languages.best_match(LANGUAGES.keys())
    return best or 'fr'


def t(key, **kwargs):
    """Raccourci pour gettext; garde la compatibilité avec l'ancien appel `t()`.

    Les messages doivent être extraits et traduits via Flask-Babel
    (`pybabel extract`, `pybabel init/compile`).
    """
    text = gettext(key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except Exception:
            pass
    return text
