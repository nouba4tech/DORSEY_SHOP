#!/usr/bin/env python
"""
Crée un produit pour chaque fichier image présent dans app/static/images/products
qui n'est pas déjà associé à un produit existant (via le slug).

Heuristiques simples :
- slug = nom de fichier sans extension
- name = slug transformé en titre
- catégorie déduite par mots-clés basiques
- prix par défaut 24_990 FCFA (modifiable via DEFAULT_PRICE)

Usage :
    python scripts/bulk_import_images.py
"""
import sys
import re
from pathlib import Path

# S'assurer que le projet est dans le PYTHONPATH
BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app import create_app
from app.models import db, Product, Category  # type: ignore

IMAGE_DIR = BASE_DIR / "app" / "static" / "images" / "products"
ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif"}
DEFAULT_PRICE = 24_990


def slugify(filename: str) -> str:
    slug = filename.lower()
    slug = re.sub(r"\.[^.]+$", "", slug)  # remove extension
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


def title_from_slug(slug: str) -> str:
    words = slug.replace("-", " ").split()
    return " ".join(w.capitalize() for w in words) or "Produit"


def guess_category_slug(slug: str) -> str:
    s = slug.lower()
    if any(k in s for k in ["basket", "shoe", "sneaker"]):
        return "chaussures"
    if any(k in s for k in ["casquette", "cap", "bonnet", "hat", "beret"]):
        return "chapeaux"
    if any(k in s for k in ["ceinture", "belt"]):
        return "accessoires"
    if any(k in s for k in ["sac", "bag", "sac-a-dos", "backpack"]):
        return "accessoires"
    if any(k in s for k in ["polo", "t-shirt", "tee-shirt", "sweat", "veste", "pull"]):
        return "hommes"
    if any(k in s for k in ["robe", "jupe"]):
        return "femmes"
    return "accessoires"


def unique_sku(slug: str, existing: set) -> str:
    base = slug.upper().replace("-", "")[:16] or "SKU"
    sku = base
    counter = 1
    while sku in existing:
        suffix = f"-{counter}"
        sku = (base[: 20 - len(suffix)] + suffix)[:20]
        counter += 1
    existing.add(sku)
    return sku


def ensure_categories():
    """Retourne un dict slug -> Category, en assumant qu'elles existent déjà."""
    categories = {c.slug: c for c in Category.query.all()}
    missing = []
    for slug in ["hommes", "femmes", "chaussures", "chapeaux", "accessoires"]:
        if slug not in categories:
            missing.append(slug)
    if missing:
        # fallback: créer minimalement
        for slug in missing:
            cat = Category(name=slug.capitalize(), slug=slug, description=slug)
            db.session.add(cat)
        db.session.commit()
        categories = {c.slug: c for c in Category.query.all()}
    return categories


def main():
    app = create_app()
    with app.app_context():
        categories = ensure_categories()
        existing_skus = {p.sku for p in Product.query.with_entities(Product.sku).all()}
        created = 0
        skipped = 0

        for file in sorted(IMAGE_DIR.iterdir()):
            if not file.is_file() or file.suffix.lower() not in ALLOWED_EXT:
                continue

            slug = slugify(file.name)
            if Product.query.filter_by(slug=slug).first():
                skipped += 1
                continue

            name = title_from_slug(slug)
            cat_slug = guess_category_slug(slug)
            category = categories.get(cat_slug) or list(categories.values())[0]

            sku = unique_sku(slug, existing_skus)

            product = Product(
                sku=sku,
                name=name,
                slug=slug,
                description=name,
                short_description=name,
                price=float(DEFAULT_PRICE),
                compare_price=None,
                is_featured=False,
                is_on_sale=False,
                sale_price=None,
                quantity=50,
                category_id=category.id,
                brand="DORSEY",
                main_image=file.name,
                sizes='["S","M","L","XL"]',
                colors='["Noir","Blanc"]',
                images=f'["{file.name}"]',
                is_active=True,
            )
            db.session.add(product)
            created += 1

        if created:
            db.session.commit()

        print(f"Créés : {created} | Ignorés (déjà présents) : {skipped}")


if __name__ == "__main__":
    main()
