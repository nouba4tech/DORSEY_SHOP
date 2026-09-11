#!/usr/bin/env python3
"""Check if .mo files contain translations."""

import os
from pathlib import Path

mo_en = Path('translations/en/LC_MESSAGES/messages.mo')
mo_ar = Path('translations/ar/LC_MESSAGES/messages.mo')

print("Checking .mo files...")
print(f"EN .mo exists: {mo_en.exists()} (size: {mo_en.stat().st_size if mo_en.exists() else 'N/A'} bytes)")
print(f"AR .mo exists: {mo_ar.exists()} (size: {mo_ar.stat().st_size if mo_ar.exists() else 'N/A'} bytes)")

# Try to read .mo file directly using gettext
print("\nTrying to load translations with gettext...")
try:
    import gettext as babel_gettext
    
    # Load English translations
    en_trans = babel_gettext.GNUTranslations(open('translations/en/LC_MESSAGES/messages.mo', 'rb'))
    print("✓ English .mo loaded")
    
    # Test translation
    result = en_trans.gettext('Accueil')
    print(f"EN: 'Accueil' → '{result}'")
    
except Exception as e:
    print(f"✗ Error loading translations: {e}")

print("\nDone.")
