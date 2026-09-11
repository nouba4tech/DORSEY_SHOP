#!/usr/bin/env python
"""
Script interactif : associer les images génériques (WhatsApp, etc.) à des produits
et les renommer avec des noms descriptifs.

Usage:
    python assign_images_to_products.py
"""
import sys
import os
from pathlib import Path
from app import create_app
from app.models import Product
import re


def slugify(text):
    """Convertir un texte en slug lisible."""
    text = str(text).lower()
    text = re.sub(r'[àâä]', 'a', text)
    text = re.sub(r'[éèêë]', 'e', text)
    text = re.sub(r'[îï]', 'i', text)
    text = re.sub(r'[ôö]', 'o', text)
    text = re.sub(r'[ùûü]', 'u', text)
    text = re.sub(r'[ç]', 'c', text)
    text = re.sub(r'\s+', '-', text.strip())
    text = re.sub(r'[^a-z0-9\-]', '', text)
    text = re.sub(r'-+', '-', text).strip('-')
    return text


def find_generic_images(folder='products'):
    """Trouver toutes les images génériques non renommées."""
    image_dir = Path('app/static/images/products')
    
    generic_keywords = ['whatsapp', 'téléchargement', 'images (', 'images.', 'image']
    generic_images = []
    
    for image_file in sorted(image_dir.glob('*')):
        if not image_file.is_file():
            continue
        
        # Vérifier si le nom est générique
        if any(keyword in image_file.name.lower() for keyword in generic_keywords):
            generic_images.append(image_file)
    
    return generic_images


def list_products(search_term=''):
    """Lister les produits disponibles avec recherche facultative."""
    query = Product.query.filter_by(is_active=True)
    
    if search_term:
        search = f"%{search_term}%"
        query = query.filter(Product.name.ilike(search))
    
    return query.order_by(Product.name).limit(20).all()


def main():
    app = create_app()
    
    with app.app_context():
        generic_images = find_generic_images()
        
        if not generic_images:
            print("✅ Aucune image générique trouvée !")
            return 0
        
        print(f"📦 {len(generic_images)} images génériques à traiter\n")
        
        renamed = 0
        skipped = 0
        
        for idx, image_file in enumerate(generic_images, 1):
            print(f"\n{'='*70}")
            print(f"[{idx}/{len(generic_images)}] {image_file.name}")
            print('='*70)
            
            # Afficher l'aperçu du fichier
            file_size_kb = image_file.stat().st_size / 1024
            print(f"📄 Taille: {file_size_kb:.1f} KB")
            
            # Demander la recherche de produit
            while True:
                search = input("\n🔍 Chercher un produit (ou 'skip'/'quit'): ").strip()
                
                if search.lower() == 'quit':
                    print(f"\n✨ {renamed} images renommées, {skipped} ignorées.")
                    return 0
                
                if search.lower() == 'skip':
                    skipped += 1
                    break
                
                # Chercher les produits
                products = list_products(search)
                
                if not products:
                    print("❌ Aucun produit trouvé. Réessayez.")
                    continue
                
                # Afficher les résultats
                print(f"\n✅ {len(products)} produit(s) trouvé(s) :\n")
                for i, product in enumerate(products, 1):
                    print(f"  {i}. {product.name}")
                    if product.sku:
                        print(f"     SKU: {product.sku}")
                
                # Choisir un produit
                choice = input("\n📌 Sélectionner un numéro (ou 'r' pour refaire la recherche): ").strip()
                
                if choice.lower() == 'r':
                    continue
                
                try:
                    product_idx = int(choice) - 1
                    if 0 <= product_idx < len(products):
                        selected_product = products[product_idx]
                        print(f"\n✨ Produit sélectionné : {selected_product.name}")
                        
                        # Générer le nouveau nom
                        product_slug = slugify(selected_product.name)
                        _, ext = os.path.splitext(image_file.name)
                        new_name = f"{product_slug}{ext}"
                        new_path = image_file.parent / new_name
                        
                        # Éviter les doublons
                        counter = 1
                        base_name = product_slug
                        while new_path.exists():
                            new_name = f"{base_name}-{counter}{ext}"
                            new_path = image_file.parent / new_name
                            counter += 1
                        
                        # Renommer le fichier
                        try:
                            image_file.rename(new_path)
                            print(f"✅ Renommé en : {new_name}")
                            renamed += 1
                            break
                        except Exception as e:
                            print(f"❌ Erreur lors du renommage : {e}")
                    else:
                        print("❌ Numéro invalide.")
                except ValueError:
                    print("❌ Entrée invalide.")
        
        print(f"\n{'='*70}")
        print(f"✨ Terminé ! {renamed} images renommées, {skipped} ignorées.")
        print('='*70)
        
        return 0


if __name__ == '__main__':
    sys.exit(main())
