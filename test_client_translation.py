#!/usr/bin/env python3
"""Test Flask-Babel with the app and test_client."""

from app import create_app
from flask import session

app = create_app()
client = app.test_client()

# Set cookies manually to test language switching  
test_cases = [
    ('en', 'Home'),  # English
    ('fr', 'Accueil'),  # French (same)
]

print("Testing translation rendering with test_client:")
for lang, expected in test_cases:
    # Make a request with language parameter
    response = client.get(f'/lang/{lang}', follow_redirects=True)
    
    # The response redirects to referrer (home)
    # Let's just check that the locale is set
    print(f"GET /lang/{lang} → Status: {response.status_code}")

# Now test rendering a template
print("\nDirect template rendering tests:")

with app.test_client() as c:
    # Set language in a request context
    with c.session_transaction() as sess:
        sess['lang'] = 'en'
    
    response = c.get('/')
    
    # Check if English text is in the response     
    if 'Home' in response.text or b'Home' in response.data:
        print("✓ English translation found in homepage")
    elif 'Accueil' in response.text or b'Accueil' in response.data:
        print("✗ French text found (translation not working)")
    else:
        print("? Could not determine translation status")
    
    # Check content-type
    print(f"Response length: {len(response.data)} bytes")
