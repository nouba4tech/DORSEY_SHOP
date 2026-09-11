from app import create_app
from app.models import db, Product

app = create_app()

with app.app_context():
    # Liste précise des IDs et nouveaux noms basés sur ce que je vois
    # ID: 383, 384, 385, 386 etc. semblent être ceux de la capture
    to_fix = {
        383: "Chemise à Carreaux Bleue",
        384: "Chemise à Carreaux Noire",
        385: "Chemise à Carreaux Rouge",
        386: "Chemise à Carreaux Bleue et Jaune",
        380: "Chemise à Carreaux Premium",
        381: "Chemise à Carreaux Marine",
        382: "Chemise à Carreaux Festive"
    }
    
    count = 0
    for pid, new_name in to_fix.items():
        p = Product.query.get(pid)
        if p:
            old_name = p.name
            p.name = new_name
            p.short_description = f"{new_name} - Collection Dorsey"
            print(f"Fixed ID {pid}: {old_name} -> {new_name}")
            count += 1
            
    db.session.commit()
    print(f"\n✅ Total : {count}")
