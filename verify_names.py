from app import create_app
from app.models import Product

app = create_app()
with app.app_context():
    products = Product.query.limit(10).all()
    print("--- FIRST 10 PRODUCTS ---")
    for p in products:
        print(f"'{p.name}' -> {p.slug}")
    
    # Let's count how many names still have digits at the end
    import re
    all_products = Product.query.all()
    have_digits = [p.name for p in all_products if re.search(r'\s\d+$', p.name)]
    print(f"\n--- PRODUCTS WITH DIGITS AT END: {len(have_digits)} ---")
    for name in have_digits[:20]:
        print(name)
