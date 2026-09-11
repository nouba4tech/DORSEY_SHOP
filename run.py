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
            
            # Créer des produits de démo
            if Product.query.count() == 0:
                cat_by_slug = {c.slug: c for c in categories}
                import json
                placeholder_img = "placeholder.jpg"
                # Jeu de démo aligné sur les fichiers présents dans app/static/images/products
                demo = [
                    ("HOM-TSH-001","T-shirt Teddy Smith Rouge","tshirt-teddy-smith-rouge","T-shirt coton rouge imprimé.",14990,"hommes","tee-shirt-coupe-droite-junior-garcon-teddy-smith-en-coton-rouge-imprime-a-la-poitrine-et-au-dos.jpg",True,False,18990),
                    ("HOM-TSH-002","T-shirt Teddy Smith Jaune","tshirt-teddy-smith-jaune","T-shirt jaune motif hamburger.",15990,"hommes","tee-shirt-coupe-droite-junior-garcon-teddy-smith-en-coton-jaune-col-rond-imprime-hamburger-a-la-poitrine-et-au-dos.jpg",False,True,18990),
                    ("HOM-SWT-003","Sweat capuche CK Noir","sweat-capuche-ck-noir","Sweat à capuche noir logo CK.",32990,"hommes","sweat-a-capuche-coupe-droite-junior-garcon-calvin-klein-jeans-en-coton-noir-avec-le-logo-imprime.jpg",True,False,None),
                    ("HOM-POL-004","Polo Boss Blanc","polo-boss-blanc","Polo maille piquée blanc.",27990,"hommes","polo-coupe-ajustee-boss-en-maille-piquee-blanc-manches-courtes-logo-carre-brode.jpg",False,False,None),
                    ("HOM-POL-005","Polo Bleu Marine Motifs","polo-bleu-marine-motifs","Polo bleu marine à motifs.",28990,"hommes","polo-coupe-regular-fit-tom-tailor-en-coton-bleu-marine-a-petits-motifs-avec-un-patch-a-la-poitrine.jpg",False,True,32990),
                    ("SHO-BAS-006","Baskets Tommy Hilfiger Marine","baskets-th-marine","Baskets ado marine patch kaki.",54990,"chaussures","-baskets-ado-tommy-hilfiger-marine-avec-patch-marron-et-vert-kaki-a-semelle-plateau.jpg",True,False,None),
                    ("SHO-BAS-007","Baskets Multicolores","baskets-multicolores","Baskets garçon multicolores.",51990,"chaussures","-baskets-garcon-tommy-hilfiger-multicolore-avec-lacets-plats-rond-et-superposition-de-patchs.jpg",False,True,57990),
                    ("ACC-SAC-008","Sac à dos Eastpak Gris","sac-a-dos-eastpak-gris","Sac à dos Eastpak Day Pak'r anthracite.",45990,"accessoires","-sac-a-dos-eastpak-day-pak-r-anthracite-chine.jpg",True,False,None),
                    ("HAT-CAP-009","Casquette Velours Noire","casquette-velours-noire","Casquette 9Forty noire velours.",19990,"chapeaux","-casquette-9forty-strapback-junior-garcon-new-era-en-coton-noire-aspect-velours-cotele.jpg",False,False,None),
                    ("HAT-CAP-010","Casquette Kaki Brodée","casquette-kaki-brodee","Casquette kaki broderie blanche.",18990,"chapeaux","-casquette-coupe-strapback-junior-garcon-new-era-en-coton-kaki-avec-broderie-blanche.jpg",False,False,None),
                    ("HAT-BON-011","Bonnet Boss Noir","bonnet-boss-noir","Bonnet maille côtelée noir.",14990,"chapeaux","-bonnet-junior-garcon-boss-noir-maille-cotelee.jpg",False,False,None),
                    ("ACC-CEI-012","Ceinture Levi's Marron","ceinture-levis-marron","Ceinture cuir marron boucle dorée.",24990,"accessoires","-ceinture-levi-s-en-cuir-marron-a-boucle-metallique-arrondie-doree.jpg",False,False,None),
                    ("ACC-CEI-013","Ceinture CK Noire","ceinture-ck-noire","Ceinture cuir de buffle noire.",25990,"accessoires","-ceinture-calvin-klein-jeans-cuir-de-buffle-noire.jpg",False,False,None),
                    ("ACC-CEI-014","Ceinture Redskins Marron","ceinture-redskins-marron","Ceinture cuir de buffle marron.",23990,"accessoires","-ceinture-redskins-cuir-de-buffle-marron-fabriquee-en-france.jpg",False,True,26990),
                    ("HOM-POL-015","Polo Tom Tailor Bleu","polo-tom-tailor-bleu","Polo coton bleu logo brodé.",26990,"hommes","polo-coupe-regular-fit-tom-tailor-en-coton-bleu-avec-le-logo-brode-en-petit.jpg",False,False,None),
                ]
                for sku, name, slug, desc, price, cat_slug, image_name, featured, on_sale, compare_price in demo:
                    p = Product(
                        sku=sku,
                        name=name,
                        slug=slug,
                        description=desc,
                        short_description=desc,
                        price=float(price),
                        compare_price=float(compare_price) if compare_price else (float(price * 1.25) if on_sale else None),
                        is_featured=bool(featured),
                        is_on_sale=bool(on_sale),
                        sale_price=float(compare_price) * 0.8 if compare_price else (float(price * 0.85) if on_sale else None),
                        quantity=50,
                        category_id=cat_by_slug[cat_slug].id,
                        brand="DORSEY",
                        main_image=image_name,
                        sizes=json.dumps(["S","M","L","XL"]),
                        colors=json.dumps(["Noir","Blanc","Orange"]),
                        images=json.dumps([image_name]),
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
