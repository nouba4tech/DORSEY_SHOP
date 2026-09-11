#!/usr/bin/env python
"""
Script pour gérer les traductions avec Flask-Babel
Initialise, extrait, compile et met à jour les fichiers de traduction

Usage:
    python manage_translations.py extract    # Extraire les messages
    python manage_translations.py init       # Initialiser les langues
    python manage_translations.py compile    # Compiler les traductions
    python manage_translations.py update     # Mettre à jour les traductions
"""
import sys
import os
import subprocess
from pathlib import Path


def run_command(cmd, description):
    """Exécuter une commande shell."""
    print(f"\n📦 {description}...")
    print(f"   Commande: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {description} réussi !")
        if result.stdout:
            print(f"   {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de {description}")
        if e.stderr:
            print(f"   {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"❌ Commande non trouvée. Assurez-vous que pybabel est installé.")
        print(f"   pip install Babel")
        return False


def extract_messages():
    """Extraire les messages du code et des templates."""
    cmd = [
        sys.executable, '-m', 'babel.messages.frontend',
        'extract',
        '-F', 'babel.cfg',
        '-o', 'messages.pot',
        '.'
    ]
    return run_command(cmd, "Extraction des messages")


def init_catalog(locale):
    """Initialiser un catalogue de traduction pour une langue."""
    cmd = [
        sys.executable, '-m', 'babel.messages.frontend',
        'init',
        '-i', 'messages.pot',
        '-d', 'translations',
        '-l', locale
    ]
    return run_command(cmd, f"Initialisation du catalogue pour {locale}")


def update_catalog():
    """Mettre à jour les catalogues existants."""
    cmd = [
        sys.executable, '-m', 'babel.messages.frontend',
        'update',
        '-i', 'messages.pot',
        '-d', 'translations'
    ]
    return run_command(cmd, "Mise à jour des catalogues")


def compile_catalogs():
    """Compiler les fichiers .po en .mo."""
    cmd = [
        sys.executable, '-m', 'babel.messages.frontend',
        'compile',
        '-d', 'translations',
        '-f'
    ]
    return run_command(cmd, "Compilation des catalogues")


def init_translations():
    """Initialiser les traductions pour en, ar."""
    print("\n🌍 Initialisation des traductions...")
    
    # Extraire d'abord
    if not extract_messages():
        return False
    
    # Initialiser les langues
    for locale in ['en', 'ar']:
        if not init_catalog(locale):
            return False
    
    print("\n✨ Traductions initialisées !")
    print("📝 Éditer les fichiers .po pour ajouter les traductions :")
    print("   - translations/en/LC_MESSAGES/messages.po")
    print("   - translations/ar/LC_MESSAGES/messages.po")
    print("\nPuis lancez : python manage_translations.py compile")
    
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python manage_translations.py extract    # Extraire les messages")
        print("  python manage_translations.py init       # Initialiser les traductions")
        print("  python manage_translations.py update     # Mettre à jour les traductions")
        print("  python manage_translations.py compile    # Compiler les traductions")
        print("  python manage_translations.py all        # Faire extract + init + compile")
        return 1
    
    command = sys.argv[1].lower()
    
    if command == 'extract':
        success = extract_messages()
    elif command == 'init':
        success = init_translations()
    elif command == 'update':
        success = update_catalog()
    elif command == 'compile':
        success = compile_catalogs()
    elif command == 'all':
        print("🚀 Initialisation complète des traductions...\n")
        success = (
            extract_messages() and
            init_translations() and
            compile_catalogs()
        )
        if success:
            print("\n🎉 Deux fois les traductions sont prêtes !")
    else:
        print(f"❌ Commande inconnue : {command}")
        return 1
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
