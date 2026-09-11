from app import create_app
from app.models import db, Product, Category
import json

app = create_app()

with app.app_context():
    data = {
        "categories": [{"id": c.id, "name": c.name} for c in Category.query.all()],
        "products": [{"id": p.id, "name": p.name, "image": p.main_image, "category": p.category.name if p.category else "N/A"} for p in Product.query.all()]
    }
    with open('data_dump.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
