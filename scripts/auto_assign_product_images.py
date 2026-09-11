#!/usr/bin/env python
"""
Assigne automatiquement des images aux produits en se basant sur le slug.

Stratégie simple :
- parcourt app/static/images/products
- choisit le fichier dont le nom contient le slug du produit (priorité si le nom commence par le slug)
- met à jour main_image et images = [fichier]

Usage :
    python scripts/auto_assign_product_images.py
"""
import os
from pathlib import Path
import sys

# Assurer que le dossier du projet est dans le PYTHONPATH avant les imports locaux
BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app import create_app
from app.models import db, Product


IMAGE_DIR = Path("app/static/images/products")
ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
PLACEHOLDER = "placeholder.jpg"


def load_files():
    files = []
    for file in IMAGE_DIR.iterdir():
        if file.is_file() and file.suffix.lower() in ALLOWED_EXT:
            files.append(file.name)
    return files


def score_match(slug: str, filename: str) -> int:
    name = filename.lower()
    slug = slug.lower()
    score = 0
    if name.startswith(slug):
        score += 5
    if slug in name:
        score += 3
    if name.replace("-", "").startswith(slug.replace("-", "")):
        score += 2
    return score


def pick_best(slug: str, files):
    best = None
    best_score = 0
    for f in files:
        sc = score_match(slug, f)
        if sc > best_score:
            best = f
            best_score = sc
    return best, best_score


def main():
    files = load_files()
    if not files:
        print("Aucune image trouvée dans", IMAGE_DIR)
        return

    app = create_app()
    with app.app_context():
        updated = 0
        no_match = 0
        products = list(Product.query.all())
        for idx, product in enumerate(products):
            best, score = pick_best(product.slug or "", files)
            if score > 0:
                chosen = best
            else:
                # Pas de correspondance : attribuer une image en round-robin pour éviter le placeholder partout
                chosen = files[idx % len(files)] if files else PLACEHOLDER

            if product.main_image != chosen:
                product.main_image = chosen
                product.images = f'["{chosen}"]'
                updated += 1
            if score == 0:
                no_match += 1

        if updated:
            db.session.commit()

        print(f"Produits mis à jour : {updated}")
        print(f"Sans correspondance (placeholder) : {no_match}")
        print(f"Total produits : {Product.query.count()}")


if __name__ == "__main__":
    main()
