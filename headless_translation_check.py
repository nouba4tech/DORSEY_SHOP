#!/usr/bin/env python3
"""Headless check: request homepage with English locale and confirm translation."""
from app import create_app

app = create_app()

def check_home(lang):
    with app.test_client() as c:
        # set session language
        with c.session_transaction() as sess:
            sess['lang'] = lang
        resp = c.get('/')
        text = resp.get_data(as_text=True)
        found = 'Home' in text
        print(f"Lang={lang} -> status={resp.status_code}, contains 'Home'?: {found}")
        # print snippet around first occurrence for debugging
        if found:
            idx = text.find('Home')
            snippet = text[max(0, idx-40): idx+40]
            print('...'+snippet+'...')
        else:
            # show top 500 chars for inspection
            print(text[:500])

if __name__ == '__main__':
    print('Checking English:')
    check_home('en')
    print('\nChecking French (control):')
    check_home('fr')
