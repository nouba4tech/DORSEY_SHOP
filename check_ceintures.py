from app import create_app
from app.models import db, Product, Category

app = create_app()

with app.app_context():
    # Rechercher les produits nommés "Ceinture"
    ceintures = Product.query.filter(Product.name.ilike('%Ceinture%')).all()
    print(f"--- TROUVÉ {len(ceintures)} PRODUITS NOMMÉS CEINTURE ---")
    for p in ceintures:
        print(f"ID: {p.id} | Name: {p.name} | Image: {p.main_image} | Category: {p.category.name if p.category else 'N/A'}")
