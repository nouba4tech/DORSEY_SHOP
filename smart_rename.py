import re
from app import create_app
from app.models import db, Product

def clean_name_from_image(filename):
    # Remove extension
    name = filename.rsplit('.', 1)[0]
    
    # Check if generic
    if re.match(r'^(images|image|whatsapp|téléchargement|100\d{4})', name.lower()):
        return None
        
    # Replace dashes and underscores with spaces
    name = name.replace('-', ' ').replace('_', ' ')
    
    # Remove common junk words or codes
    name = re.sub(r'\s*\d{5,}\s*', ' ', name) # Remove long ID numbers like 1005980
    name = re.sub(r'\s*v\d+\s*', ' ', name, flags=re.I) # Remove version tags like V1
    name = re.sub(r'\s*\(.*\)\s*', ' ', name) # Remove (1), (2), etc.
    
    # Remove specific details to keep it concise but descriptive
    # We want "Polo BOSS Blanc" instead of "Polo coupe ajustee boss en maille piquee blanc manches courtes logo carre brode"
    
    words = name.split()
    if not words:
        return None
        
    # Keep the first few words if it's very long, or try to detect brand
    brands = ['boss', 'levis', 'levi s', 'teddy smith', 'tommy hilfiger', 'calvin klein', 'ck', 'redskins', 'eastpak', 'new era', 'eden park', 'tom tailor']
    
    clean_words = []
    found_brand = None
    for brand in brands:
        if brand in name.lower():
            found_brand = brand.title()
            break
            
    # Start with product type
    types = ['t shirt', 'tee shirt', 'polo', 'sweat', 'chemise', 'costume', 'pantalon', 'jean', 'chino', 'cargo', 'manteau', 'veste', 'casquette', 'bonnet', 'ceinture', 'sac', 'baskets', 'chaussures', 'culotte']
    
    found_type = None
    for t in types:
        if t in name.lower().replace('-', ' '):
            found_type = t.title()
            break
            
    # Special cases for names starting with -
    name_clean = name.strip(' -')
    
    # Try to extract color
    colors = ['noir', 'blanc', 'bleu', 'marine', 'rouge', 'vert', 'jaune', 'marron', 'gris', 'kaki', 'multicolore', 'anthracite']
    found_color = None
    for color in colors:
        if color in name.lower():
            found_color = color.title()
            break
            
    # Reconstruct a nice name
    result = []
    if found_type:
        result.append(found_type)
    if found_brand:
        result.append(found_brand)
    if found_color:
        result.append(found_color)
        
    if len(result) >= 2:
        return " ".join(result)
        
    # Fallback to a cleaned version of the original name if we couldn't be smart
    cleaned = " ".join(name_clean.split()[:5]).title()
    if len(cleaned) < 3:
        return None
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
        renamed_count = 0
        
        seen_slugs = {}
        
        for p in products:
            old_name = p.name
            suggested_name = clean_name_from_image(p.main_image)
            
            if not suggested_name:
                suggested_name = old_name
            
            base_slug = slugify(suggested_name)
            
            # Handle duplicates
            if base_slug in seen_slugs:
                seen_slugs[base_slug] += 1
                new_name = f"{suggested_name} {seen_slugs[base_slug]}"
                new_slug = f"{base_slug}-{seen_slugs[base_slug]}"
            else:
                seen_slugs[base_slug] = 1
                new_name = suggested_name
                new_slug = base_slug
            
            if new_name != old_name or p.slug != new_slug:
                p.name = new_name
                p.slug = new_slug
                if "Produit" in (p.short_description or ""):
                    p.short_description = f"{new_name} - Collection DORSEY"
                
                print(f"Renaming: '{old_name}' -> '{new_name}' (Slug: {new_slug})")
                renamed_count += 1
                
        try:
            db.session.commit()
            print(f"Total renamed: {renamed_count}")
        except Exception as e:
            db.session.rollback()
            print(f"Error during commit: {e}")

if __name__ == '__main__':
    main()
