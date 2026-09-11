#!/usr/bin/env python3
"""
Add basic English and Arabic translations to the .po files.
This script provides translations for common UI strings.
"""

import re
from pathlib import Path

# Basic French to English translations
TRANSLATIONS_EN = {
    "Catalogue - DORSEY-SHOP": "Catalog - DORSEY-SHOP",
    "À Propos - DORSEY-SHOP": "About - DORSEY-SHOP",
    "Panier": "Cart",
    "Passer la commande": "Checkout",
    "Accueil": "Home",
    "Connexion": "Login",
    "Inscription": "Register",
    "Mon profil": "My Profile",
    "Déconnexion": "Logout",
    "Recherche": "Search",
    "Rechercher un article...": "Search for an item...",
    "Tri": "Sort",
    "Prix": "Price",
    "Ajouter au panier": "Add to Cart",
    "Appliquer": "Apply",
    "Réinitialiser": "Reset",
    "Confirmer": "Confirm",
    "Annuler": "Cancel",
    "Supprimer": "Delete",
    "Modifier": "Edit",
    "Enregistrer": "Save",
    "Chargement...": "Loading...",
    "Erreur": "Error",
    "Succès": "Success",
    "Attention": "Warning",
    "Plus d'informations": "More Information",
    "Retour": "Back",
    "Suivant": "Next",
    "Précédent": "Previous",
    "Accueil": "Home",
    "Produits": "Products",
    "À propos": "About",
    "Contact": "Contact",
    "Aide": "Help",
    "Conditions d'utilisation": "Terms of Use",
    "Politique de confidentialité": "Privacy Policy",
    "Mentions légales": "Legal Notice",
}

# Basic French to Arabic translations (transliterated/English approximations for demo)
TRANSLATIONS_AR = {
    "Catalogue - DORSEY-SHOP": "الكتالوج - DORSEY-SHOP",
    "À Propos - DORSEY-SHOP": "حول - DORSEY-SHOP",
    "Panier": "السلة",
    "Passer la commande": "الدفع",
    "Accueil": "الرئيسية",
    "Connexion": "تسجيل الدخول",
    "Inscription": "التسجيل",
    "Mon profil": "ملفي",
    "Déconnexion": "تسجيل الخروج",
    "Recherche": "بحث",
    "Rechercher un article...": "ابحث عن عنصر...",
    "Tri": "الفرز",
    "Prix": "السعر",
    "Ajouter au panier": "أضف إلى السلة",
    "Appliquer": "تطبيق",
    "Réinitialiser": "إعادة تعيين",
    "Confirmer": "تأكيد",
    "Annuler": "إلغاء",
    "Supprimer": "حذف",
    "Modifier": "تعديل",
    "Enregistrer": "حفظ",
    "Chargement...": "جاري التحميل...",
    "Erreur": "خطأ",
    "Succès": "نجاح",
    "Attention": "تحذير",
    "Plus d'informations": "المزيد من المعلومات",
    "Retour": "رجوع",
    "Suivant": "التالي",
    "Précédent": "السابق",
    "Produits": "المنتجات",
    "À propos": "حول",
    "Contact": "اتصال",
    "Aide": "مساعدة",
}

def update_po_file(po_path: Path, translations: dict):
    """Update a .po file with French to target language translations."""
    
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # For each available translation
    for fr_text, target_text in translations.items():
        # Escape special characters for regex
        escaped_fr = re.escape(fr_text)
        
        # Pattern to find msgid followed by msgstr (with empty translation)
        # Handles both single-line and multi-line strings
        pattern = rf'(msgid "{escaped_fr}"\nmsgstr )""'
        replacement = rf'\1"{target_text}"'
        
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
    
    with open(po_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Updated {po_path.relative_to('.')}")

def main():
    base_path = Path('translations')
    
    en_po = base_path / 'en' / 'LC_MESSAGES' / 'messages.po'
    ar_po = base_path / 'ar' / 'LC_MESSAGES' / 'messages.po'
    
    if not en_po.exists():
        print(f"✗ File not found: {en_po}")
        return
    
    if not ar_po.exists():
        print(f"✗ File not found: {ar_po}")
        return
    
    print("Adding basic translations...")
    update_po_file(en_po, TRANSLATIONS_EN)
    update_po_file(ar_po, TRANSLATIONS_AR)
    
    print("\n✓ Translations added successfully!")
    print("Next steps:")
    print("1. Review the .po files for accuracy")
    print("2. Run: pybabel compile -d translations")

if __name__ == '__main__':
    main()
