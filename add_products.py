"""
Script pour ajouter de nouveaux produits à partir des images du dossier products
"""
from app import create_app
from app.models import db, Product, Category
import os
import json
from pathlib import Path

app = create_app()

def slugify(text):
    """Convertir un texte en slug valide"""
    import re
    text = str(text).lower()
    text = re.sub(r'[àâä]', 'a', text)
    text = re.sub(r'[éèêë]', 'e', text)
    text = re.sub(r'[îï]', 'i', text)
    text = re.sub(r'[ôö]', 'o', text)
    text = re.sub(r'[ùûü]', 'u', text)
    text = re.sub(r'[ç]', 'c', text)
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = text.strip('-')
    return text

def get_category_for_image(filename):
    """Déterminer la catégorie basée sur le nom du fichier"""
    filename_lower = filename.lower()
    
    # Déterminer la catégorie basée sur les mots-clés
    if any(word in filename_lower for word in ['tee', 'shirt', 'sweat', 'hoodie', 't-shirt']):
        return 'hommes'
    elif any(word in filename_lower for word in ['casquette', 'bonnet', 'cap', 'hat']):
        return 'chapeaux'
    elif any(word in filename_lower for word in ['ceinture', 'belt']):
        return 'accessoires'
    elif any(word in filename_lower for word in ['chaussure', 'shoe', 'sneaker', 'boot', 'sandale']):
        return 'chaussures'
    elif any(word in filename_lower for word in ['sac', 'bag', 'sacoche']):
        return 'accessoires'
    elif any(word in filename_lower for word in ['chemise']):
        return 'hommes'
    elif any(word in filename_lower for word in ['culotte']):
        return 'femmes'
    else:
        return 'accessoires'  # Catégorie par défaut

def add_new_products():
    """Ajouter les nouveaux produits à la base de données"""
    with app.app_context():
        products_dir = Path('app/static/images/products')
        
        # Images déjà existantes (exclure celles-ci)
        existing_images = [
            '1005980_11234_V1.avif',
            '1006783_18001_V1.webp',
            '1007342_10124_V1.avif',
            '1008031_10524_V1.avif',
            '1008031_18000_V1.avif',
            '1008037_10000_V1.avif',
            '1008037_18000_V1.webp',
            '1008204_18424_V11.avif',
            '1008205_11325_V11.avif',
            '1008207_11315_V11.avif',
            '1008208_14800_V11.avif',
            '1008320_11303_V11.avif',
            '1008320_12088_V11.avif',
            '1008322_16707_V11.avif',
            '1008535_11044_V11.avif',
            '1008536_14506_V11.avif',
            '1005025_10505_V11.webp',
        ]
        
        # Récupérer toutes les catégories
        categories = Category.query.all()
        cat_by_slug = {c.slug: c for c in categories}
        
        # Vérifier les fichiers images
        for image_file in sorted(products_dir.glob('*')):
            if image_file.name in existing_images:
                continue
            
            if image_file.name == 'README.md':
                continue
            
            if not image_file.is_file():
                continue
            
            # Vérifier si un produit existe déjà pour cette image
            existing = Product.query.filter_by(main_image=image_file.name).first()
            if existing:
                print(f"⏭️  Produit existant: {existing.name} ({image_file.name})")
                continue
            
            # Créer le nom du produit à partir du nom du fichier
            product_name = image_file.stem.replace('-', ' ').replace('_', ' ').title()
            product_slug = slugify(product_name)
            
            # Déterminer la catégorie
            category_slug = get_category_for_image(image_file.name)
            category = cat_by_slug.get(category_slug)
            
            if not category:
                print(f"⚠️  Catégorie non trouvée: {category_slug}")
                continue
            
            # Générer un SKU unique
            sku = f"NEW-{image_file.stem[:20].upper()}"
            
            # Vérifier que le SKU est unique
            existing_sku = Product.query.filter_by(sku=sku).first()
            if existing_sku:
                sku = f"NEW-{image_file.name.replace('.', '-')[:20].upper()}"
            
            # Créer le produit
            product = Product(
                sku=sku,
                name=product_name,
                slug=product_slug,
                description=f"Produit {product_name} - Article exclusif DORSEY-SHOP",
                short_description=f"Produit {product_name}",
                price=34.90,  # Prix par défaut
                compare_price=None,
                quantity=10,  # Stock initial
                category_id=category.id,
                brand="DORSEY",
                main_image=image_file.name,
                images=json.dumps([image_file.name]),
                sizes=json.dumps(["S", "M", "L", "XL"]),
                colors=json.dumps(["Noir", "Blanc"]),
                is_active=True,
                is_featured=False,
                is_on_sale=False,
            )
            
            db.session.add(product)
            print(f"✅ Nouveau produit ajouté: {product.name} ({image_file.name})")
        
        # Sauvegarder
        try:
            db.session.commit()
            print(f"\n✅ Tous les produits ont été ajoutés avec succès!")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Erreur lors de l'ajout des produits: {e}")

if __name__ == '__main__':
    add_new_products()
