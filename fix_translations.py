import re
from pathlib import Path
import subprocess

# Expanded translations
TRANSLATIONS_EN = {
    "Accueil": "Home",
    "Catalogue": "Catalog",
    "À Propos": "About",
    "À propos": "About",
    "À Propos de DORSEY": "About DORSEY",
    "Contact": "Contact",
    "Contacts": "Contacts",
    "Aide": "Help",
    "Connexion": "Login",
    "Inscription": "Register",
    "Panier": "Cart",
    "Recherche": "Search",
    "Tri": "Sort",
    "Prix": "Price",
    "Produits": "Products",
    "Ajouter au panier": "Add to Cart",
    "Passer la commande": "Checkout",
    "Appliquer": "Apply",
    "Réinitialiser": "Reset",
    "Confirmer": "Confirm",
    "Annuler": "Cancel",
    "Supprimer": "Delete",
    "Modifier": "Edit",
    "Enregistrer": "Save",
    "Mon profil": "My Profile",
    "Déconnexion": "Logout",
    "Se connecter": "Sign In",
    "S'inscrire": "Sign Up",
    "Mot de passe": "Password",
    "Email": "Email",
    "Adresse": "Address",
    "Téléphone": "Phone",
    "Nom complet": "Full Name",
    "Commande": "Order",
    "Commandes": "Orders",
    "Quantité": "Quantity",
    "Sous-total": "Subtotal",
    "Total": "Total",
    "Livraison": "Shipping",
    "Gratuit": "Free",
    "Réduction": "Discount",
    "Code promo": "Promo Code",
    "Paiement": "Payment",
    "En stock": "In Stock",
    "Rupture de stock": "Out of Stock",
    "Bienvenue": "Welcome",
    "Merci": "Thank You",
    "Oui": "Yes",
    "Non": "No",
    "Tous droits réservés.": "All rights reserved.",
    "Suivez-nous": "Follow us",
    "Liens utiles": "Useful Links",
    "Qui sommes-nous ?": "Who are we?",
    "Nous contacter": "Contact us",
    "Explorer le catalogue": "Explore the catalog",
    "DORSEY-SHOP - Mode et accessoires au Tchad": "DORSEY-SHOP - Fashion and accessories in Chad",
    "Boutique": "Shop",
    "Compte": "Account",
    "Mon compte": "My account",
    "Nos services": "Our services",
    "Newsletter": "Newsletter",
    "Saisir votre mail": "Enter your email",
    "Une boutique mode simple, fiable et orientée qualité.": "A simple, reliable and quality-oriented fashion boutique.",
    "Essayez une autre recherche ou retirez certains filtres.": "Try another search or remove some filters.",
    "Voir tout le catalogue": "View all catalog",
    "Supprimer la recherche": "Delete search",
    "Sélection adaptée à vos filtres.": "Selection adapted to your filters.",
    "Il vous reste %(num)d article à découvrir": "You have %(num)d item left to discover",
    "Il vous reste %(num)d articles à découvrir": "You have %(num)d items left to discover",
}

TRANSLATIONS_AR = {
    "Accueil": "الرئيسية",
    "Catalogue": "الكتالوج",
    "À Propos": "حول",
    "À propos": "حول",
    "À Propos de DORSEY": "حول دورسي",
    "Contact": "اتصال",
    "Contacts": "اتصالات",
    "Aide": "مساعدة",
    "Connexion": "تسجيل الدخول",
    "Inscription": "التسجيل",
    "Panier": "السلة",
    "Recherche": "بحث",
    "Tri": "الفرز",
    "Prix": "السعر",
    "Produits": "المنتجات",
    "Ajouter au panier": "أضف إلى السلة",
    "Passer la commande": "الدفع",
    "Appliquer": "تطبيق",
    "Réinitialiser": "إعادة تعيين",
    "Confirmer": "تأكيد",
    "Annuler": "إلغاء",
    "Supprimer": "حذف",
    "Modifier": "تعديل",
    "Enregistrer": "حفظ",
    "Mon profil": "ملفي الشخصي",
    "Déconnexion": "تسجيل الخروج",
    "Se connecter": "دخول",
    "S'inscrire": "تسجيل",
    "Mot de passe": "كلمة المرور",
    "Email": "البريد الإلكتروني",
    "Adresse": "العنوان",
    "Téléphone": "الهاتف",
    "Nom complet": "الاسم الكامل",
    "Commande": "الطلب",
    "Commandes": "الطلبات",
    "Quantité": "الكمية",
    "Sous-total": "المجموع الفرعي",
    "Total": "المجموع",
    "Livraison": "الشحن",
    "Gratuit": "مجاني",
    "Réduction": "خصم",
    "Code promo": "كود الخصم",
    "Paiement": "الدفع",
    "En stock": "في المخزن",
    "Rupture de stock": "نفذت الكمية",
    "Bienvenue": "مرحباً",
    "Merci": "شكراً",
    "Oui": "نعم",
    "Non": "لا",
    "Tous droits réservés.": "جميع الحقوق محفوظة.",
    "Suivez-nous": "تابعنا",
    "Liens utiles": "روابط مفيدة",
    "Qui sommes-nous ?": "من نحن؟",
    "Nous contacter": "اتصل بنا",
    "Explorer le catalogue": "استكشف الكتالوج",
    "La référence de la mode au Tchad.": "مرجع الموضة في تشاد.",
    "Collections exclusives et style incomparable.": "مجموعات حصرية وأسلوب لا يضاهى.",
    "Inspirations de la boutique": "إلهامات المتجر",
    "DORSEY-SHOP - Mode et accessoires au Tchad": "دورسي شوب - الموضة والإكسسوارات في تشاد",
    "Boutique": "المتجر",
    "Compte": "الحساب",
    "Mon compte": "حسابي",
    "Nos services": "خدماتنا",
    "Newsletter": "النشرة الإخبارية",
    "Saisir votre mail": "أدخل بريدك الإلكتروني",
    "Une boutique mode simple, fiable et orientée qualité.": "بوتيك أزياء بسيط وموثوق وموجه نحو الجودة.",
    "Essayez une autre recherche ou retirez certains filtres.": "حاول البحث مرة أخرى أو قم بإزالة بعض الفلاتر.",
    "Voir tout le catalogue": "عرض الكتالوج بالكامل",
    "Supprimer la recherche": "حذف البحث",
    "Sélection adaptée à vos filtres.": "الاختيار المناسب للفلاتر الخاصة بك.",
    "Il vous reste %(num)d article à découvrir": "بقي لديك عنصر %(num)d لاكتشافه",
    "Il vous reste %(num)d articles à découvrir": "بقي لديك %(num)d عناصر لاكتشافها",
}

def update_po(po_path, translations):
    if not po_path.exists():
        return
    
    with open(po_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    i = 0
    updated = 0
    while i < len(lines):
        line = lines[i]
        
        # Remove fuzzy marker if we are about to translate this entry
        if line.startswith('#, fuzzy'):
            peek = i + 1
            while peek < len(lines) and lines[peek].startswith('#'):
                peek += 1
            if peek < len(lines) and lines[peek].startswith('msgid "'):
                msgid = lines[peek][7:-2]
                if msgid in translations:
                    # Skip the fuzzy line
                    i += 1
                    line = lines[i]
        
        new_lines.append(line)
        
        # Singular msgid
        if line.startswith('msgid "') and not line.startswith('msgid ""') and (i + 1 >= len(lines) or not lines[i+1].startswith('msgid_plural')):
            msgid = line[7:-2]
            if i + 1 < len(lines) and lines[i+1].startswith('msgstr '):
                msgstr = lines[i+1][8:-2]
                if msgstr == "" or msgstr == msgid:
                    if msgid in translations:
                        new_lines[len(new_lines)-1] = line
                        new_lines.append(f'msgstr "{translations[msgid]}"\n')
                        i += 2
                        updated += 1
                        continue
        
        # Plural msgid
        if line.startswith('msgid "') and i + 1 < len(lines) and lines[i+1].startswith('msgid_plural'):
            msgid_singular = line[7:-2]
            msgid_plural = lines[i+1][14:-2]
            
            # Find all msgstr[n]
            j = i + 2
            plural_indices = []
            while j < len(lines) and lines[j].startswith('msgstr['):
                plural_indices.append(j)
                j += 1
            
            if plural_indices:
                # Check if any are empty or same as original
                is_empty = any(lines[idx].split('"', 1)[1].strip('" \n') == "" for idx in plural_indices)
                if is_empty:
                    if msgid_singular in translations and msgid_plural in translations:
                        new_lines.append(f'msgid_plural "{msgid_plural}"\n')
                        for idx_pos, line_idx in enumerate(plural_indices):
                            val = translations[msgid_singular] if idx_pos == 0 else translations[msgid_plural]
                            new_lines.append(f'msgstr[{idx_pos}] "{val}"\n')
                        
                        i = j # Skip the indices we processed
                        updated += 1
                        continue

        i += 1
    
    with open(po_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    return updated

def main():
    base = Path('translations')
    en_path = base / 'en' / 'LC_MESSAGES' / 'messages.po'
    ar_path = base / 'ar' / 'LC_MESSAGES' / 'messages.po'
    
    print(f"Checking {en_path}...")
    en_updated = update_po(en_path, TRANSLATIONS_EN)
    print(f"Checking {ar_path}...")
    ar_updated = update_po(ar_path, TRANSLATIONS_AR)
    
    print(f"Updated EN: {en_updated}")
    print(f"Updated AR: {ar_updated}")
    
    # Compile
    print("Compiling catalogs...")
    subprocess.run(['venv/Scripts/pybabel', 'compile', '-d', 'translations'])
    print("Done.")

if __name__ == "__main__":
    main()
