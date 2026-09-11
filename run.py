"""
Point d'entrée de DORSEY-SHOP
"""
from app import create_app
import os

# Créer l'application
app = create_app()

def init_database():
    """Initialiser la base de données avec des données de test"""
    from app.models import db, Category, Product, User
    from werkzeug.security import generate_password_hash
    
    with app.app_context():
        # Créer toutes les tables
        db.create_all()
        
        # Vérifier si la base est vide
        if Category.query.count() == 0:
            print("Initialisation de la base de données...")
            
            # Créer les catégories principales
            categories = [
                Category(name="Hommes", slug="hommes", description="Vêtements pour hommes"),
                Category(name="Femmes", slug="femmes", description="Vêtements pour femmes"),
                Category(name="Chaussures", slug="chaussures", description="Chaussures hommes et femmes"),
                Category(name="Chapeaux", slug="chapeaux", description="Chapeaux et casquettes"),
                Category(name="Accessoires", slug="accessoires", description="Accessoires de mode"),
                Category(name="Nouveautés", slug="nouveautes", description="Nouveaux arrivages"),
                Category(name="Promotions", slug="promotions", description="Articles en promotion"),
            ]
            
            for category in categories:
                db.session.add(category)
            
            # Créer un admin par défaut
            admin = User(
                username="admin",
                email="admin@dorsey-shop.com",
                password_hash=generate_password_hash("admin123"),
                is_admin=True
            )
            db.session.add(admin)
            
            # Créer un utilisateur test
            user = User(
                username="client",
                email="client@dorsey-shop.com",
                password_hash=generate_password_hash("client123"),
                is_admin=False
            )
            db.session.add(user)
            
            # Créer le catalogue de produits à partir du jeu de données
            # vérifié (nom, image et catégorie cohérents) dans
            # app/seed_data/products.json
            if Product.query.count() == 0:
                cat_by_slug = {c.slug: c for c in categories}
                import json
                seed_path = os.path.join(
                    os.path.dirname(__file__), 'app', 'seed_data', 'products.json'
                )
                with open(seed_path, encoding='utf-8') as f:
                    seed_products = json.load(f)

                for item in seed_products:
                    category = cat_by_slug.get(item['category_slug'])
                    if not category:
                        continue
                    p = Product(
                        sku=item['sku'],
                        name=item['name'],
                        slug=item['slug'],
                        description=item['description'],
                        short_description=item['short_description'],
                        price=float(item['price']),
                        compare_price=float(item['compare_price']) if item.get('compare_price') else None,
                        is_featured=bool(item['is_featured']),
                        is_on_sale=bool(item['is_on_sale']),
                        sale_price=float(item['sale_price']) if item.get('sale_price') else None,
                        quantity=item['quantity'],
                        category_id=category.id,
                        brand=item['brand'],
                        main_image=item['main_image'],
                        sizes=json.dumps(item['sizes']),
                        colors=json.dumps(item['colors']),
                        images=json.dumps(item['images']),
                        is_active=True,
                    )
                    db.session.add(p)
            
            db.session.commit()
            print(" Base de données initialisée avec succès!")
            print(" Admin: admin@dorsey-shop.com / admin123")
            print(" Client: client@dorsey-shop.com / client123")

if __name__ == '__main__':
    # Initialiser la base au démarrage
    init_database()
    
    # Lancer l'application
    print("Lancement de DORSEY-SHOP sur http://localhost:5000")
    print(f"Base de données: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"Mode debug: {app.config['DEBUG']}")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )
