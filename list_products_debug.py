from app import create_app
from app.models import db, Product, Category

app = create_app()

with app.app_context():
    products = Product.query.all()
    print(f"Total products: {len(products)}")
    for p in products:
        print(f"ID: {p.id} | Name: {p.name} | Image: {p.main_image} | Category: {p.category.name if p.category else 'N/A'}")
