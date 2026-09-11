import re
from app import create_app
from app.models import db, Product

def clean_name_from_image(filename):
    name = filename.rsplit('.', 1)[0]
    # Si c'est un nom générique, on retourne None pour garder le nom actuel (déjà nettoyé)
    if re.match(r'^(images|image|whatsapp|téléchargement|100\d{4})', name.lower()):
        return None
        
    name = name.replace('-', ' ').replace('_', ' ')
    # Suppression des IDs longs et versions
    name = re.sub(r'\s*\d{5,}\s*', ' ', name)
    name = re.sub(r'\s*v\d+\s*', ' ', name, flags=re.I)
    name = re.sub(r'\s*\(.*\)\s*', ' ', name)
    
    brands = ['boss', 'levis', 'levi s', 'teddy smith', 'tommy hilfiger', 'calvin klein', 'ck', 'redskins', 'eastpak', 'new era', 'eden park', 'tom tailor']
    found_brand = None
    for brand in brands:
        if brand in name.lower():
            found_brand = brand.title()
            break
            
    types = ['t shirt', 'tee shirt', 'polo', 'sweat', 'chemise', 'costume', 'pantalon', 'jean', 'chino', 'cargo', 'manteau', 'veste', 'casquette', 'bonnet', 'ceinture', 'sac', 'baskets', 'chaussures', 'culotte']
    found_type = None
    for t in types:
        if t in name.lower().replace('-', ' '):
            found_type = t.title()
            break
            
    name_clean = name.strip(' -')
    colors = ['noir', 'blanc', 'bleu', 'marine', 'rouge', 'vert', 'jaune', 'marron', 'gris', 'kaki', 'multicolore', 'anthracite']
    found_color = None
    for color in colors:
        if color in name.lower():
            found_color = color.title()
            break
            
    result = []
    if found_type: result.append(found_type)
    if found_brand: result.append(found_brand)
    if found_color: result.append(found_color)
        
    if len(result) >= 2:
        return " ".join(result)
        
    cleaned = " ".join(name_clean.split()[:5]).title()
    # Enlever les chiffres à la fin si présents dans le nom nettoyé
    cleaned = re.sub(r'\s+\d+$', '', cleaned)
    if len(cleaned) < 3: return None
    return cleaned

def slugify(text):
    text = str(text).lower()
    text = re.sub(r'[àâä]', 'a', text)
    text = re.sub(r'[éèêë]', 'e', text)
    text = re.sub(r'[îï]', 'i', text)
    text = re.sub(r'[ôö]', 'o', text)
    text = re.sub(r'[ùûü]', 'u', text)
    text = re.sub(r'[ç]', 'c', text)
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def main():
    app = create_app()
    with app.app_context():
        products = Product.query.all()
        
        # Phase 1: Reset provisoire des slugs
        for i, p in enumerate(products):
            p.slug = f"tmp-{i}-{p.id}"
        db.session.flush()
        
        # Phase 2: Renommage sans chiffres dans le NOM, mais avec chiffres dans le SLUG pour l'unicité
        renamed_count = 0
        seen_slugs = set()
        
        for p in products:
            suggested_name = clean_name_from_image(p.main_image)
            if not suggested_name:
                # Si pas de suggestion, on prend le nom actuel et on retire les chiffres à la fin
                suggested_name = re.sub(r'\s+\d+$', '', p.name)
            
            # Nettoyage final du nom suggéré au cas où
            suggested_name = re.sub(r'\s+\d+$', '', suggested_name)
            
            base_slug = slugify(suggested_name)
            
            final_name = suggested_name # Le nom reste propre
            final_slug = base_slug
            counter = 1
            
            # Seul le SLUG devient unique avec des chiffres si nécessaire
            while final_slug in seen_slugs:
                counter += 1
                final_slug = f"{base_slug}-{counter}"
            
            seen_slugs.add(final_slug)
            
            p.name = final_name
            p.slug = final_slug
            
            # Mise à jour des descriptions et meta
            if "Produit" in (p.short_description or "") or " - " in (p.short_description or ""):
                p.short_description = f"{final_name} - Collection DORSEY"
            p.meta_title = f"{final_name} | DORSEY-SHOP"
            
            renamed_count += 1
                
        try:
            db.session.commit()
            print(f"✅ Nettoyage terminé ! {renamed_count} produits mis à jour sans chiffres dans les noms.")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erreur: {e}")

if __name__ == '__main__':
    main()
