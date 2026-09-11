#!/usr/bin/env python3
"""Direct test - check if Flask-Babel can load translations."""

from flask import Flask
from flask_babel import Babel, gettext

app = Flask(__name__)
app.config['BABEL_DEFAULT_LOCALE'] = 'fr'
app.config['BABEL_SUPPORTED_LOCALES'] = ['fr', 'en', 'ar']
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'

babel = Babel(app)

@babel.localeselector
def get_lang():
    from flask import session
    lang = session.get('lang', 'fr')
    return lang if lang in ['fr', 'en', 'ar'] else 'fr'

with app.test_request_context():
    from flask import session
    session['lang'] = 'en'
    
    result_en = gettext('Accueil')
    print(f"EN: 'Accueil' → '{result_en}'")
    
    session['lang'] = 'fr'
    result_fr = gettext('Accueil')
    print(f"FR: 'Accueil' → '{result_fr}'")
