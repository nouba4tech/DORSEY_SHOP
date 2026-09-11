#!/usr/bin/env python
"""
Met en place un référentiel fixe de catégories et applique un mapping explicite
type -> catégorie aux produits existants.

Catégories cibles (slug) : hommes, femmes, chaussures, chapeaux, accessoires, sous-vetements.

Règles de détection de type (tokens du nom/slug/image) :
    - chemise, shirt           -> Chemise       (hommes)
    - veste (croisée etc.)     -> Veste         (hommes)
    - polo                     -> Polo          (hommes)
    - t-shirt/tee              -> T-shirt       (hommes)
    - sweat/hoodie             -> Sweat         (hommes)
    - manteau/coat             -> Manteau       (hommes)
    - ceinture/belt            -> Ceinture      (accessoires)
    - sac/bag/backpack         -> Sac           (accessoires)
    - baskets/sneakers/shoes   -> Baskets       (chaussures)
    - casquette/cap            -> Casquette     (chapeaux)
    - bonnet/beanie            -> Bonnet        (chapeaux)
    - beret                    -> Béret         (chapeaux)
    - robe/dress               -> Robe          (femmes)
    - jupe/skirt               -> Jupe          (femmes)
    - boxer/caleçon/slip       -> Sous-vêtement (sous-vetements)

Heuristique de renommage : on renomme le produit si son nom est générique
("Accessoire", "Chapeau", "Chaussures", "Vêtement", "Sous-vêtement", "Produit").

Usage :
    python scripts/fix_categories_and_types.py
"""
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app import create_app  # type: ignore
from app.models import db, Product, Category  # type: ignore


ALLOWED_CATEGORIES = [
    ("hommes", "Hommes", "Mode hommes"),
    ("femmes", "Femmes", "Mode femmes"),
    ("chaussures", "Chaussures", "Chaussures"),
    ("chapeaux", "Chapeaux", "Chapeaux & casquettes"),
    ("accessoires", "Accessoires", "Accessoires"),
    ("sous-vetements", "Sous-vêtements", "Sous-vêtements"),
]

TYPE_RULES = [
    ({"chemise", "shirt"}, "Chemise", "hommes"),
    ({"veste", "blazer"}, "Veste", "hommes"),
    ({"polo"}, "Polo", "hommes"),
    ({"t", "tee", "tshirt", "t-shirt", "tee-shirt"}, "T-shirt", "hommes"),
    ({"sweat", "hoodie", "capuche"}, "Sweat", "hommes"),
    ({"manteau", "coat", "pardessus"}, "Manteau", "hommes"),
    ({"ceinture", "belt"}, "Ceinture", "accessoires"),
    ({"sac", "bag", "backpack", "sacoche"}, "Sac", "accessoires"),
    ({"basket", "baskets", "sneaker", "sneakers", "shoe", "shoes"}, "Baskets", "chaussures"),
    ({"casquette", "cap"}, "Casquette", "chapeaux"),
    ({"bonnet", "beanie"}, "Bonnet", "chapeaux"),
    ({"beret", "béret", "berets"}, "Béret", "chapeaux"),
    ({"robe", "dress"}, "Robe", "femmes"),
    ({"jupe", "skirt"}, "Jupe", "femmes"),
    ({"boxer", "calecon", "caleçon", "slip", "culotte", "lingerie"}, "Sous-vêtement", "sous-vetements"),
]

GENERIC_NAMES = {"Accessoire", "Chapeau", "Chaussures", "Vêtement", "Sous-vêtement", "Produit", "Chemise"}


def tokenize(text: str) -> set[str]:
    return {tok for tok in re.split(r"[-_\\s]+", (text or "").lower()) if tok}


def ensure_categories():
    existing = {c.slug: c for c in Category.query.all()}
    changed = False
    for slug, name, desc in ALLOWED_CATEGORIES:
        if slug not in existing:
            cat = Category(slug=slug, name=name, description=desc, is_active=True)
            db.session.add(cat)
            changed = True
        else:
            cat = existing[slug]
            if not cat.is_active:
                cat.is_active = True
                changed = True
    if changed:
        db.session.commit()
    return {c.slug: c for c in Category.query.all()}


def detect_type(tokens: set[str]):
    for kws, type_name, cat_slug in TYPE_RULES:
        if kws & tokens:
            return type_name, cat_slug
    return None, None


def main():
    app = create_app()
    with app.app_context():
        categories = ensure_categories()
        updated = 0

        products = Product.query.all()
        for p in products:
            source = p.main_image or p.slug or p.name or ""
            tokens = tokenize(source)
            type_name, cat_slug = detect_type(tokens)

            # Catégorie : si détectée, on applique
            if cat_slug and cat_slug in categories:
                p.category_id = categories[cat_slug].id

            # Nom : renommer seulement si générique et type trouvé
            if type_name and (p.name in GENERIC_NAMES):
                p.name = type_name
                p.short_description = type_name
                if not p.description or p.description in GENERIC_NAMES:
                    p.description = type_name

            updated += 1

        db.session.commit()
        print(f"Produits traités : {updated}")


if __name__ == "__main__":
    main()
