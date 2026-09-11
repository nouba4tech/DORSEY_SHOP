from app import create_app
from app.models import db, Product

app = create_app()

with app.app_context():
    # Liste de produits identifiés manuellement comme erronés (votre capture d'écran)
    # On va chercher les produits par leur image pour être sûr
    images_erronees = [
        'chemise-carrelee1.jpg',
        'chemise-carrelee2.jpg',
        'chemise-carrelee3.jpg',
        'chemise-carrelee4.jpg',
        'chemise-a-carreaux-bleue.jpg',
        'chemise-a-carreaux-rouge-et-noire.jpg'
    ]
    
    # On va aussi chercher tous les produits "Ceinture" et vérifier leur image
    problèmes = Product.query.filter(Product.name.ilike('Ceinture%')).all()
    count = 0
    
    for p in problèmes:
        img = p.main_image.lower()
        if 'chemise' in img or 'shirt' in img or 'jean' in img:
            old_name = p.name
            if 'carreau' in img or 'carrelee' in img:
                p.name = "Chemise à Carreaux"
            elif 'jean' in img:
                p.name = "Jean Slim"
            else:
                p.name = "Chemise Premium"
            
            p.short_description = f"{p.name} - Collection Dorsey"
            print(f"Corrected: {p.id} | {old_name} -> {p.name} (Image: {p.main_image})")
            count += 1
            
    db.session.commit()
    print(f"\n✅ Total corriger : {count}")
