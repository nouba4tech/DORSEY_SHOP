#!/usr/bin/env python3
"""Test that translations are actually served in different languages."""

from app import create_app
from flask import render_template_string, g

app = create_app()

# Test data: (French text, Expected English, Expected Arabic fallback)
test_cases = [
    ("Accueil", "Home", "Accueil"),
    ("Catalogue", "Catalog", "Catalogue"),
    ("Panier", "Cart", "Panier"),
    ("Ajouter au panier", "Add to Cart", "Ajouter au panier"),
    ("Passer la commande", "Checkout", "Passer la commande"),
]

def test_language(lang_code, language_name):
    """Test translation for a specific language."""
    print(f"\n{'='*50}")
    print(f"Testing {language_name} ({lang_code})")
    print(f"{'='*50}")
    
    with app.test_request_context(headers={'Accept-Language': lang_code}):
        # Manually set the locale for testing
        from app.i18n import get_lang
        from babel.core import Locale
        from flask import session
        
        session['lang'] = lang_code
        
        success_count = 0
        for fr_text, en_expected, ar_fallback in test_cases:
            # Render template with translation
            template = f"{{{{ _({repr(fr_text)}) }}}}"
            result = render_template_string(template)
            
            if lang_code == 'en':
                expected = en_expected
                status = "✓" if result == expected else "✗"
                print(f"{status} '{fr_text}' → '{result}' (expected: '{expected}')")
                if result == expected:
                    success_count += 1
            elif lang_code == 'ar':
                # Arabic should get French text as fallback for now
                status = "✓" if result == ar_fallback else "✗"
                print(f"{status} '{fr_text}' → '{result}' (expected: '{ar_fallback}')")
                if result == ar_fallback:
                    success_count += 1
            else:  # French
                status = "✓" if result == fr_text else "✗"
                print(f"{status} '{fr_text}' → '{result}' (stays same)")
                if result == fr_text:
                    success_count += 1
        
        print(f"\nSuccess rate: {success_count}/{len(test_cases)} ({100*success_count//len(test_cases)}%)")
        return success_count == len(test_cases)

# Run tests
print("\n" + "="*50)
print("TRANSLATION TEST SUITE")
print("="*50)

fr_ok = test_language('fr', 'Français (Default)')
en_ok = test_language('en', 'English')
ar_ok = test_language('ar', 'العربية (Arabic)')

print("\n" + "="*50)
print("SUMMARY")
print("="*50)
if fr_ok:
    print("✓ French translations working")
else:
    print("✗ French translations NOT working")

if en_ok:
    print("✓ English translations working")
else:
    print("✗ English translations NOT working")

if ar_ok:
    print("✓ Arabic fallback working (French text)")
else:
    print("✗ Arabic fallback NOT working")

print("="*50)
if fr_ok and en_ok:
    print("✅ Translations are WORKING correctly!")
else:
    print("⚠️ Some translations need fixes")
