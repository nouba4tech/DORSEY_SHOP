#!/usr/bin/env python
"""
Nettoie les produits existants :
- Génère des slugs courts à partir des noms de fichiers image
- Crée des noms courts (max 3 mots) lisibles
- Fixe des prix réalistes pour le marché tchadien par catégorie
- Désactive les promos incohérentes
- Évite les noms génériques type "WhatsApp Image ..."

Usage :
    python scripts/normalize_products.py
"""
import re
import sys
from pathlib import Path

# Assurer le PYTHONPATH
BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app import create_app  # type: ignore
from app.models import db, Product, Category  # type: ignore

PRICE_BY_CATEGORY = {
    "hommes": 25000,
    "femmes": 28000,
    "chaussures": 60000,
    "chapeaux": 15000,
    "accessoires": 12000,
    "sous-vetements": 15000,
}

FALLBACK_PRICE = 20000

# Nom par catégorie
BASE_NAME_BY_CAT = {
    "chapeaux": "Chapeau",
    "chaussures": "Chaussures",
    "accessoires": "Accessoire",
    "hommes": "Vêtement",
    "femmes": "Vêtement",
    "sous-vetements": "Sous-vêtement",
}

# Règles de nommage par type (priorité dans l'ordre)
TYPE_RULES = [
    ({"manteau", "coat", "pardessus"}, "Manteau", "hommes"),
    ({"sweat", "hoodie", "capuche"}, "Sweat", "hommes"),
    ({"polo"}, "Polo", "hommes"),
    ({"t", "tee", "tshirt", "tee-shirt", "t-shirt"}, "T-shirt", "hommes"),
    ({"chemise", "shirt"}, "Chemise", "hommes"),
    ({"costume", "suit", "smoking"}, "Costume", "hommes"),
    ({"ceinture", "belt"}, "Ceinture", "accessoires"),
    ({"sacados", "backpack", "sac-a-dos", "sac", "bag", "sacoche"}, "Sac", "accessoires"),
    ({"sneaker", "sneakers", "basket", "baskets"}, "Baskets", "chaussures"),
    ({"shoe", "shoes", "loafer", "loafers", "mocassin", "mocassins", "derby", "richelieu"}, "Mocassins", "chaussures"),
    ({"casquette", "cap"}, "Casquette", "chapeaux"),
    ({"bonnet", "beanie"}, "Bonnet", "chapeaux"),
    ({"beret", "béret", "berets"}, "Béret", "chapeaux"),
    ({"robe", "dress"}, "Robe", "femmes"),
    ({"jupe", "skirt"}, "Jupe", "femmes"),
    ({"boxer", "calecon", "caleçon", "slip", "culotte", "lingerie"}, "Sous-vêtement", "sous-vetements"),
    ({"lunette", "lunettes", "sunglasses"}, "Lunettes", "accessoires"),
    ({"montre", "watch"}, "Montre", "accessoires"),
]

# Mots clés -> catégorie
TOKEN_CATEGORIES = {
    "chaussures": {"basket", "baskets", "sneaker", "sneakers", "shoe", "shoes", "loafer", "loafers", "mocassin", "mocassins", "derby", "richelieu"},
    "chapeaux": {"casquette", "casquettes", "bonnet", "bonnets", "beret", "berets", "hat", "caps", "cap", "chapeau", "chapeaux"},
    "accessoires": {"ceinture", "ceintures", "belt", "belts", "sac", "sacs", "bag", "bags", "backpack", "sac-a-dos", "sacados"},
    "hommes": {"polo", "t", "t-shirt", "tee", "tee-shirt", "sweat", "veste", "pull", "chemise", "blazer", "costume", "suit", "smoking"},
    "femmes": {"robe", "robes", "jupe", "jupes"},
    "sous-vetements": {"sous", "vetement", "vetements", "sous-vetement", "sous-vetements", "boxer", "boxers", "calecon", "caleçons", "lingerie", "slip", "culotte", "culottes"},
}

# Mots à ignorer pour générer les titres
STOPWORDS = {
    "coupe", "junior", "garcon", "garçon", "en", "et", "avec", "la", "le", "les", "des",
    "du", "de", "pour", "tailor", "tom", "teddy", "smith", "calvin", "klein", "jeans",
    "tommy", "hilfiger", "regular", "fit", "piquee", "pique", "maille", "coton",
    "manches", "courtes", "logo", "carre", "brode", "brodee", "noir", "noire", "bleu",
    "blanc", "marron", "jaune", "rouge", "vert", "gris", "marine", "fille",
    "boy", "girl", "anthracite", "chine", "strapback", "trucker"
}


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\.[^.]+$", "", text)  # remove extension
    text = re.sub(r"[^a-z0-9]+", "-", text)
    base = text.strip("-") or "produit"
    # raccourcir à 6 mots max pour éviter les slugs interminables
    parts = base.split("-")
    base_short = "-".join(parts[:6]) if len(parts) > 6 else base
    return base_short or "produit"


def short_title(slug: str) -> str:
    words = [w for w in slug.replace("-", " ").split() if w and w not in STOPWORDS]
    trimmed = words[:3] if words else slug.replace("-", " ").split()[:3]
    return " ".join(w.capitalize() for w in trimmed) or "Produit"


def guess_category_slug(slug: str) -> str:
    tokens = [t for t in re.split(r'[-_ ]+', slug.lower()) if t]
    for cat, words in TOKEN_CATEGORIES.items():
        if any(tok in words for tok in tokens):
            return cat
    return "accessoires"


def detect_type(slug: str) -> tuple[str | None, str | None]:
    tokens = set(t for t in re.split(r'[-_ ]+', slug.lower()) if t)

    # Cas spécial veste croisée: besoin de 'veste' ET (croise|double)
    if "veste" in tokens or "blazer" in tokens:
        if {"croise", "croisee", "double", "doublebreasted", "double-breasted"} & tokens:
            return "Veste croisée", "hommes"
        return "Veste", "hommes"

    for keywords, name, cat in TYPE_RULES:
        if keywords & tokens:
            return name, cat
    return None, None


def unique_slug(base: str, taken: set) -> str:
    slug = base
    i = 1
    while slug in taken:
        slug = f"{base}-{i}"
        i += 1
    taken.add(slug)
    return slug


def main():
    app = create_app()
    with app.app_context():
        taken_slugs = {p.slug for p in Product.query.with_entities(Product.slug).all()}
        updated = 0
        seq_by_cat = {}

        categories = {c.slug: c for c in Category.query.all()}
        # Créer la catégorie sous-vetements si manquante
        if "sous-vetements" not in categories:
            new_cat = Category(name="Sous-vêtements", slug="sous-vetements", description="Sous-vêtements")
            db.session.add(new_cat)
            db.session.commit()
            categories = {c.slug: c for c in Category.query.all()}

        for p in Product.query.all():
            img = (p.main_image or "").strip()
            raw_source = img or p.slug or p.name or "produit"
            raw_lower = raw_source.lower()

            # Règle spécifique pour les imports WhatsApp du 13/02/2026 (ceintures)
            if "whatsapp image 2026-02-13" in raw_lower or "whatsapp-image-2026-02-13" in raw_lower:
                base = "ceinture"
                cat_slug = "accessoires"
                forced_type = "Ceinture"
                forced_color = None
            else:
                base = slugify(raw_source)
                cat_slug = p.category.slug if p.category else guess_category_slug(base)
                forced_type = None
                forced_color = None

            # Si nom de fichier contient whatsapp -> nom générique lisible par catégorie
            if "whatsapp" in base:
                cat_slug = guess_category_slug(base)
                seq_by_cat[cat_slug] = seq_by_cat.get(cat_slug, 0) + 1
                base = f"{cat_slug}-produit-{seq_by_cat[cat_slug]:03d}"

            new_slug = unique_slug(base, taken_slugs) if p.slug != base else p.slug
            if cat_slug not in categories:
                cat_slug = guess_category_slug(base)
            target_price = PRICE_BY_CATEGORY.get(cat_slug, FALLBACK_PRICE)

            # Nom = type détecté ou libellé de catégorie + couleur si connue
            type_name, type_cat = detect_type(base)
            if forced_type:
                type_name = forced_type
            if type_cat:
                cat_slug = type_cat

            base_name = type_name or BASE_NAME_BY_CAT.get(cat_slug, "Produit")
            display_name = base_name

            # Associer la catégorie résolue
            target_cat = categories.get(cat_slug) or categories.get("accessoires")
            if target_cat:
                p.category_id = target_cat.id

            p.slug = new_slug
            p.name = display_name
            p.short_description = display_name
            p.description = p.description or display_name
            p.price = float(target_price)
            p.compare_price = None
            p.is_on_sale = False
            p.sale_price = None
            # Nettoyer les couleurs (on ne veut plus afficher/porter la couleur)
            p.colors = "[]"

            updated += 1

        if updated:
            db.session.commit()

        print(f"Produits mis à jour : {updated}")


if __name__ == "__main__":
    main()
