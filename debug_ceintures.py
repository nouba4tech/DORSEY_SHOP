from app import create_app
from app.models import Product

app = create_app()
with app.app_context():
    # Cherchons les produits qui ont "Ceinture" dans le nom (même avec des espaces)
    test = Product.query.filter(Product.name.contains('Ceinture')).all()
    print(f"Total containing 'Ceinture': {len(test)}")
    for p in test[:20]:
        print(f"ID: {p.id} | Name: '{p.name}' | Image: {p.main_image}")
