"""
Utilitaires pour la gestion des images
Normalisation, sécurisation et optimisation des noms de fichiers
"""
import os
import re
from pathlib import Path
from werkzeug.utils import secure_filename
from datetime import datetime
from flask import current_app


def normalize_filename(filename, prefix=''):
    """Normaliser un nom de fichier en slug lisible.
    
    Exemples:
    - "WhatsApp Image 2026-02-13 at 22.52.05.jpeg" → "2026021322520500.jpeg"
    - "Pantalon chino slim.jpg" → "pantalon-chino-slim.jpg"
    - Avec prefix: "produit-123-pantalon-chino.jpg"
    
    Args:
        filename: Nom du fichier à normaliser
        prefix: Préfixe optionnel (ex: slug du produit)
    
    Returns:
        Nouveau nom de fichier normalisé
    """
    # Séparer nom et extension
    name, ext = os.path.splitext(filename)
    ext = ext.lower()
    
    # Si c'est un fichier WhatsApp/Téléchargement générique, utiliser timestamp
    if any(x in name.lower() for x in ['whatsapp', 'téléchargement', 'image', 'images', 'photo']):
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        # Compter les fichiers existants pour éviter les doublons
        counter = 1
        normalized = f"{prefix}{timestamp}{counter:02d}{ext}" if prefix else f"{timestamp}{counter:02d}{ext}"
        return normalized
    
    # Sinon, slugifier le nom existant
    # Convertir caractères accentués
    name = name.lower()
    name = re.sub(r'[àâä]', 'a', name)
    name = re.sub(r'[éèêë]', 'e', name)
    name = re.sub(r'[îï]', 'i', name)
    name = re.sub(r'[ôö]', 'o', name)
    name = re.sub(r'[ùûü]', 'u', name)
    name = re.sub(r'[ç]', 'c', name)
    
    # Remplacer espaces et caractères spéciaux par des tirets
    name = re.sub(r'\s+', '-', name.strip())
    name = re.sub(r'[^a-z0-9\-]', '', name)
    name = re.sub(r'-+', '-', name).strip('-')
    
    # Ajouter le préfixe si fourni
    if prefix:
        name = f"{prefix}-{name[:30]}"  # Limiter la longueur
    
    return f"{name}{ext}"


def save_uploaded_image(file, folder='products', product_name=''):
    """Sauvegarder une image uploadée avec un nom normalisé.
    
    Args:
        file: Objet FileStorage de Flask
        folder: Dossier de destination (products, uploads, etc.)
        product_name: Nom du produit pour préfixe (optionnel)
    
    Returns:
        Tuple (success: bool, filename: str, error: str)
    """
    if not file or file.filename == '':
        return False, '', 'Aucun fichier fourni'
    
    # Vérifier l'extension
    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'webp'})
    ext = os.path.splitext(file.filename)[1].lower().lstrip('.')
    
    if ext not in allowed_extensions:
        return False, '', f'Extension non autorisée : {ext}'
    
    # Normaliser le nom de fichier
    prefix = ''
    if product_name:
        # Générer un slug du nom du produit
        prefix = product_name.lower()
        prefix = re.sub(r'[àâä]', 'a', prefix)
        prefix = re.sub(r'[éèêë]', 'e', prefix)
        prefix = re.sub(r'[^a-z0-9\s]', '', prefix)
        prefix = re.sub(r'\s+', '-', prefix.strip())[:20]
    
    filename = normalize_filename(file.filename, prefix=prefix)
    
    # Sécuriser le nom de fichier
    filename = secure_filename(filename)
    
    # Créer le chemin d'accès
    upload_folder = os.path.join(
        current_app.config.get('UPLOAD_FOLDER', 'app/static/images/uploads'),
        folder
    )
    os.makedirs(upload_folder, exist_ok=True)
    
    filepath = os.path.join(upload_folder, filename)
    
    # Éviter les doublons
    counter = 1
    base_name, ext = os.path.splitext(filename)
    while os.path.exists(filepath):
        filename = f"{base_name}-{counter}{ext}"
        filepath = os.path.join(upload_folder, filename)
        counter += 1
    
    try:
        file.save(filepath)
        return True, filename, ''
    except Exception as e:
        return False, '', str(e)


def list_product_images(product_id_or_slug, folder='products'):
    """Lister toutes les images d'un produit.
    
    Args:
        product_id_or_slug: ID ou slug du produit
        folder: Dossier de recherche
    
    Returns:
        Liste des noms de fichiers correspondant
    """
    search_prefix = str(product_id_or_slug).lower()
    upload_folder = os.path.join(
        current_app.config.get('UPLOAD_FOLDER', 'app/static/images/uploads'),
        folder
    )
    
    try:
        images = [
            f for f in os.listdir(upload_folder)
            if f.lower().startswith(search_prefix)
        ]
        return sorted(images)
    except Exception:
        return []


def rename_generic_images(folder='products', dry_run=False):
    """Renommer les fichiers d'images génériques (WhatsApp, etc.) avec des noms normalisés.
    
    Utile pour nettoyer une collection d'images existantes.
    
    Args:
        folder: Dossier à traiter
        dry_run: Si True, afficher les changements sans les appliquer
    
    Returns:
        Dict avec statistiques des renommages
    """
    image_dir = Path(current_app.config.get('UPLOAD_FOLDER', 'app/static/images/uploads')) / folder
    
    if not image_dir.exists():
        return {'error': f'Dossier non trouvé : {image_dir}', 'renamed': 0}
    
    stats = {'renamed': 0, 'errors': 0, 'changes': []}
    
    for image_file in image_dir.glob('*'):
        if not image_file.is_file():
            continue
        
        # Vérifier si le nom est générique
        if not any(x in image_file.name.lower() for x in ['whatsapp', 'téléchargement', 'image', 'images', 'screenshot', 'photo']):
            continue
        
        new_name = normalize_filename(image_file.name)
        new_path = image_file.parent / new_name
        
        change_info = {'old': image_file.name, 'new': new_name}
        stats['changes'].append(change_info)
        
        if not dry_run:
            try:
                image_file.rename(new_path)
                stats['renamed'] += 1
            except Exception as e:
                stats['errors'] += 1
                change_info['error'] = str(e)
        else:
            stats['renamed'] += 1
    
    return stats
