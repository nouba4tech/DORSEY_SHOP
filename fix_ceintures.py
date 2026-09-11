import re
from app import create_app
from app.models import db, Product, Category

app = create_app()

def slugify(text):
    text = str(text).lower()
    import re
    text = re.sub(r'[àâä]', 'a', text)
    text = re.sub(r'[éèêë]', 'e', text)
    text = re.sub(r'[îï]', 'i', text)
    text = re.sub(r'[ôö]', 'o', text)
    text = re.sub(r'[ùûü]', 'u', text)
    text = re.sub(r'[ç]', 'c', text)
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

with app.app_context():
    # Trouver tous les produits nommés "Ceinture" qui ne ressemblent pas à une ceinture dans l'image
    products = Product.query.filter(Product.name == 'Ceinture').all()
    
    corrections = 0
    cat_hommes = Category.query.filter_by(slug='hommes').first()
    
    for p in products:
        img_lower = p.main_image.lower()
        new_name = None
        
        # Détecter si c'est une chemise
        if any(w in img_lower for w in ['chemise', 'shirt', 'carreau', 'carrelee']):
            # Essayer d'extraire des infos de l'image
            color = ""
            if 'bleu' in img_lower: color = " Bleue"
            elif 'rouge' in img_lower: color = " Rouge"
            elif 'noir' in img_lower: color = " Noire"
            
            if 'carreau' in img_lower or 'carrelee' in img_lower:
                new_name = f"Chemise à Carreaux{color}"
            else:
                new_name = f"Chemise{color} Premium"
                
            p.category_id = cat_hommes.id if cat_hommes else p.category_id
            
        elif any(w in img_lower for w in ['pantalon', 'jean', 'chino', 'cargo']):
            new_name = "Pantalon Premium"
            p.category_id = cat_hommes.id if cat_hommes else p.category_id
            
        if new_name:
            print(f"Fixing: ID {p.id} | '{p.name}' -> '{new_name}' (Image: {p.main_image})")
            p.name = new_name
            # Unicité du slug
            base_slug = slugify(new_name)
            p.slug = f"{base_slug}-{p.id}"
            p.short_description = f"{new_name} - Collection Dorsey"
            corrections += 1
            
    db.session.commit()
    print(f"\n✅ Terminé : {corrections} produits corrigés.")
