#!/usr/bin/env python
"""
Script de maintenance : renommer les fichiers d'images génériques (WhatsApp, etc.)
avec des noms normalisés et descriptifs.

Usage:
    python rename_images.py [--dry-run] [--folder products]
"""
import sys
import os
from pathlib import Path
from app import create_app
from app.utils.images import rename_generic_images

def main():
    app = create_app()
    
    with app.app_context():
        dry_run = '--dry-run' in sys.argv
        folder = 'products'
        
        # Parser les arguments
        for arg in sys.argv[1:]:
            if arg.startswith('--folder='):
                folder = arg.split('=')[1]
        
        print(f"🔄 Nettoyage des images dans : {folder}")
        print(f"   Mode : {'Simulation (aucun changement)' if dry_run else 'Réel (changements appliqués)'}")
        print()
        
        stats = rename_generic_images(folder=folder, dry_run=dry_run)
        
        if 'error' in stats:
            print(f"❌ Erreur : {stats['error']}")
            return 1
        
        print(f"📊 Statistiques :")
        print(f"   ✅ Fichiers à renommer : {stats['renamed']}")
        print(f"   ❌ Erreurs : {stats['errors']}")
        print()
        
        if stats['changes']:
            print("📋 Changements :")
            for change in stats['changes'][:20]:  # Afficher les 20 premiers
                error = f" ⚠️  {change['error']}" if 'error' in change else ""
                print(f"   {change['old']} → {change['new']}{error}")
            
            if len(stats['changes']) > 20:
                print(f"   ... et {len(stats['changes']) - 20} autres fichiers")
        else:
            print("✅ Aucun fichier générique trouvé !")
        
        print()
        if dry_run:
            print("💡 Pour appliquer les changements, lancez :")
            print(f"   python rename_images.py --folder={folder}")
        else:
            print(f"✨ {stats['renamed']} fichiers ont été renommés avec succès !")
        
        return 0

if __name__ == '__main__':
    sys.exit(main())
