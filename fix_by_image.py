from app import create_app
from app.models import db, Product

app = create_app()

with app.app_context():
    # Cherchons les produits par ID car les noms ont peut-être un petit détail (espace, etc.)
    # ou cherchons tous les produits dont l'image contient 'chemise' mais qui ne s'appellent pas 'Chemise'
    problèmes = Product.query.filter(Product.main_image.ilike('%chemise%')).all()
    count = 0
    
    for p in problèmes:
        if "Ceinture" in p.name:
            old_name = p.name
            if "carreau" in p.main_image.lower() or "carrelee" in p.main_image.lower():
                p.name = "Chemise à Carreaux"
            else:
                p.name = "Chemise Premium"
            print(f"ID: {p.id} | {old_name} -> {p.name} | Image: {p.main_image}")
            count += 1
            
    db.session.commit()
    print(f"\n✅ Total : {count}")
