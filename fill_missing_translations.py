#!/usr/bin/env python3
"""
Auto-fill missing translations with intelligent fallbacks.
Uses predefined translations for common strings, falls back to French text for others.
"""

import re
from pathlib import Path

# Comprehensive English translations dictionary
EN_TRANSLATIONS = {
    # Navigation & UI
    "Accueil": "Home",
    "Catalogue": "Catalog",
    "À propos": "About",
    "Contact": "Contact",
    "Aide": "Help",
    "Connexion": "Login",
    "Inscription": "Register",
    "Panier": "Cart",
    "Recherche": "Search",
    "Tri": "Sort",
    "Filtre": "Filter",
    "Prix": "Price",
    "Produits": "Products",
    "Catégories": "Categories",

    # Buttons & Actions
    "Ajouter au panier": "Add to Cart",
    "Passer la commande": "Checkout",
    "Appliquer": "Apply",
    "Réinitialiser": "Reset",
    "Confirmer": "Confirm",
    "Annuler": "Cancel",
    "Supprimer": "Delete",
    "Modifier": "Edit",
    "Enregistrer": "Save",
    "Fermer": "Close",
    "Retour": "Back",
    "Suivant": "Next",
    "Précédent": "Previous",
    "Quitter": "Exit",
    "Continuer": "Continue",
    "Chercher": "Search",
    "Découvrir": "Discover",
    "Voir plus": "See More",
    "Charger plus": "Load More",
    "Actualiser": "Refresh",
    "Télécharger": "Download",

    # Account & Authentication
    "Mon profil": "My Profile",
    "Déconnexion": "Logout",
    "Se connecter": "Sign In",
    "S'inscrire": "Sign Up",
    "Mot de passe": "Password",
    "Email": "Email",
    "Adresse": "Address",
    "Téléphone": "Phone",
    "Prénom": "First Name",
    "Nom": "Last Name",
    "Nom complet": "Full Name",

    # Shopping
    "Commande": "Order",
    "Commandes": "Orders",
    "Quantité": "Quantity",
    "Sous-total": "Subtotal",
    "Total": "Total",
    "Livraison": "Shipping",
    "Estimation": "Estimate",
    "Gratuit": "Free",
    "Réduction": "Discount",
    "Code promo": "Promo Code",
    "Paiement": "Payment",
    "Délivré": "Delivered",
    "En attente": "Pending",
    "Annulée": "Cancelled",
    "En préparation": "Processing",
    "Remboursé": "Refunded",

    # Status & Messages
    "Erreur": "Error",
    "Succès": "Success",
    "Attention": "Warning",
    "Information": "Information",
    "Chargement": "Loading",
    "Chargement...": "Loading...",
    "Pas de résultat": "No results",
    "Non disponible": "Unavailable",
    "Disponible": "Available",
    "En stock": "In Stock",
    "Rupture de stock": "Out of Stock",

    # Time & Date
    "Aujourd'hui": "Today",
    "Hier": "Yesterday",
    "Semaine": "Week",
    "Mois": "Month",
    "Année": "Year",
    "Janvier": "January",
    "Février": "February",
    "Mars": "March",
    "Avril": "April",
    "Mai": "May",
    "Juin": "June",
    "Juillet": "July",
    "Août": "August",
    "Septembre": "September",
    "Octobre": "October",
    "Novembre": "November",
    "Décembre": "December",

    # Common Phrases
    "Bienvenue": "Welcome",
    "Merci": "Thank You",
    "S'il vous plaît": "Please",
    "Oui": "Yes",
    "Non": "No",
    "Ok": "OK",
    "Ou": "Or",
    "Et": "And",
    "De": "Of",
    "À": "To",
    "Pour": "For",
    "Avec": "With",
    "Sans": "Without",
    "Plus": "More",
    "Moins": "Less",
    "Nouveau": "New",
    "Ancien": "Old",
    "Grand": "Large",
    "Petit": "Small",
    "Cher": "Expensive",
    "Bon marché": "Cheap",
    "Cher": "Dear",
    "Bien": "Good",
    "Mal": "Bad",
    "Facile": "Easy",
    "Difficile": "Difficult",
    "Rapide": "Fast",
    "Lent": "Slow",

    # Pages & Sections
    "Accueil": "Home",
    "À Propos": "About",
    "À Propos - DORSEY-SHOP": "About - DORSEY-SHOP",
    "Catalogue - DORSEY-SHOP": "Catalog - DORSEY-SHOP",
    "Panier - DORSEY-SHOP": "Cart - DORSEY-SHOP",
    "Conditions d'utilisation": "Terms of Use",
    "Politique de confidentialité": "Privacy Policy",
    "Mentions légales": "Legal Notice",
    "Plan du site": "Sitemap",
}

def smart_translate(french_text):
    """Intelligently translate French text to English."""
    # Strip whitespace for matching
    text_lower = french_text.strip().lower()
    text_stripped = french_text.strip()
    
    # Exact match
    if text_stripped in EN_TRANSLATIONS:
        return EN_TRANSLATIONS[text_stripped]
    
    # Case-insensitive exact match
    for fr, en in EN_TRANSLATIONS.items():
        if fr.lower() == text_lower:
            return en
    
    # Partial match (for longer strings with small variations)
    for fr, en in EN_TRANSLATIONS.items():
        if len(fr) > 5 and fr.lower() in text_lower:
            return text_stripped  # Return original if partial match
    
    # Default: return French text as fallback (better than empty string)
    return text_stripped

def fill_translations(po_path: Path, translations_dict: dict):
    """Fill in missing translations in a .po file."""
    with open(po_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    result = []
    i = 0
    filled_count = 0
    
    while i < len(lines):
        line = lines[i]
        result.append(line)
        
        # Look for msgid lines
        if line.startswith('msgid "') and not line.startswith('msgid ""'):
            # Extract the French text
            match = re.match(r'msgid "(.+)"', line)
            if match:
                french_text = match.group(1)
                
                # Check if next line is an empty msgstr
                if i + 1 < len(lines) and lines[i + 1].strip() == 'msgstr ""':
                    # Get translation
                    translation = smart_translate(french_text)
                    
                    # Replace the empty msgstr with translated text
                    result.append(f'msgstr "{translation}"\n')
                    i += 2
                    filled_count += 1
                    continue
        
        i += 1
    
    # Write back
    with open(po_path, 'w', encoding='utf-8') as f:
        f.writelines(result)
    
    return filled_count

def main():
    base_path = Path('translations')
    
    en_po = base_path / 'en' / 'LC_MESSAGES' / 'messages.po'
    ar_po = base_path / 'ar' / 'LC_MESSAGES' / 'messages.po'
    
    if not en_po.exists():
        print(f"✗ File not found: {en_po}")
        return
    
    print("Filling missing English translations...")
    en_count = fill_translations(en_po, EN_TRANSLATIONS)
    print(f"✓ Filled {en_count} English translations")
    
    # For Arabic, just use French as fallback (better than empty)
    print("Filling missing Arabic translations (French fallback)...")
    ar_count = fill_translations(ar_po, {})
    print(f"✓ Filled {ar_count} Arabic translations (fallback)")
    
    print("\nRecompiling translations...")
    import subprocess
    result = subprocess.run([
        'c:\\Users\\nouba\\Desktop\\dorsey-shop\\venv\\Scripts\\pybabel',
        'compile', '-d', 'translations'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ Translations compiled successfully")
        print(f"\n✓ Translation update complete!")
        print(f"  - English: {en_count} translations filled")
        print(f"  - Arabic: {ar_count} translations filled (fallback)")
    else:
        print(f"✗ Compilation failed: {result.stderr}")

if __name__ == '__main__':
    main()
