from app import create_app
from app.models import db, Product, Category

app = create_app()

with app.app_context():
    categories = Category.query.all()
    print("CATEGORIES:")
    for c in categories:
        print(f"ID: {c.id} | Name: {c.name} | Slug: {c.slug}")
        
    print("\nPRODUCTS SAMPLE:")
    products = Product.query.limit(20).all()
    for p in products:
        print(f"ID: {p.id} | Name: {p.name} | Image: {p.main_image} | Category: {p.category.name if p.category else 'N/A'}")
