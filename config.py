"""
Configuration de DORSEY-SHOP
Boutique de vêtements hommes, femmes, chaussures et accessoires
"""
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def _get_database_url():
    """
    Retourne l'URL de base de données.
    - Priorité à DATABASE_URL si définie.
    - Sinon, fallback SQLite dans instance/dev.db (ou /tmp en environnement
      serverless en lecture seule, ex. Vercel).
    """
    db_url = os.environ.get('DATABASE_URL')
    if os.environ.get('DEBUG_DB_PATH'):
        raise RuntimeError(f"DEBUG env DATABASE_URL={db_url!r} cwd={os.getcwd()!r} env_has_dotenv_file={os.path.exists('.env')!r}")
    if db_url:
        return db_url
    base_dir = os.path.abspath(os.path.dirname(__file__))
    instance_path = os.path.join(base_dir, 'instance')

    def _writable(path):
        try:
            os.makedirs(path, exist_ok=True)
            probe = os.path.join(path, '.write_test')
            with open(probe, 'w') as f:
                f.write('x')
            os.remove(probe)
            return True
        except OSError:
            return False

    writable = _writable(instance_path)
    if not writable:
        # Système de fichiers en lecture seule (ex. Vercel) : seul /tmp est
        # inscriptible. Les données ne persisteront pas entre les invocations.
        import tempfile
        instance_path = os.path.join(tempfile.gettempdir(), 'dorsey-instance')
        os.makedirs(instance_path, exist_ok=True)
    sqlite_path = os.path.join(instance_path, 'dev.db')
    if os.environ.get('DEBUG_DB_PATH'):
        raise RuntimeError(
            f"DEBUG base_dir={base_dir} first_probe_writable={writable} "
            f"final_instance_path={instance_path} sqlite_path={sqlite_path} "
            f"path_exists={os.path.exists(instance_path)}"
        )
    return 'sqlite:///' + sqlite_path.replace('\\', '/')

class Config:
    """
    Configuration de base de l'application
    """
    
    # ====================
    # INFORMATIONS BOUTIQUE
    # ====================
    SHOP_NAME = "DORSEY-SHOP"
    SHOP_DESCRIPTION = "Boutique de mode hommes, femmes, chaussures et accessoires"
    SHOP_SLOGAN = "Style & Élégance au Quotidien"
    SHOP_VERSION = "1.0.0"
    
    # ====================
    # SÉCURITÉ
    # ====================
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-dorsey-shop-2024-change-in-production'
    
    # ====================
    # BASE DE DONNÉES
    # ====================
    SQLALCHEMY_DATABASE_URI = _get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # Mettre à True pour debug les requêtes SQL
    
    # ====================
    # UPLOAD & FICHIERS
    # ====================
    # Dossier pour les uploads
    UPLOAD_FOLDER = os.path.join('app', 'static', 'images', 'uploads')
    
    # Taille maximum des fichiers uploadés (16MB)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
    # Extensions autorisées pour les images
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # ====================
    # PAGINATION
    # ====================
    PRODUCTS_PER_PAGE = 12
    ORDERS_PER_PAGE = 20
    CUSTOMERS_PER_PAGE = 15
    
    # ====================
    # CONTACT & COORDONNÉES
    # ====================
    SHOP_EMAIL = os.environ.get('SHOP_EMAIL', 'contact@boutique-ndjamena.td')
    SHOP_PHONE = os.environ.get('SHOP_PHONE', '+235 22 51 23 45')
    SHOP_ADDRESS = os.environ.get('SHOP_ADDRESS', 'Avenue Charles de Gaulle, Quartier Chagoua')
    SHOP_CITY = "N'Djamena"
    SHOP_COUNTRY = "Tchad"
    
    # ====================
    # RÉSEAUX SOCIAUX
    # ====================
    FACEBOOK_URL = os.environ.get('FACEBOOK_URL', '#')
    INSTAGRAM_URL = os.environ.get('INSTAGRAM_URL', '#')
    TWITTER_URL = os.environ.get('TWITTER_URL', '#')
    TIKTOK_URL = os.environ.get('TIKTOK_URL', '#')
    PINTEREST_URL = os.environ.get('PINTEREST_URL', '#')
    
    # ====================
    # GESTION STOCK
    # ====================
    LOW_STOCK_THRESHOLD = 5
    OUT_OF_STOCK_THRESHOLD = 0
    
    # ====================
    # LIVRAISON
    # ====================
    SHIPPING_COST_STANDARD = 4.90
    SHIPPING_COST_EXPRESS = 9.90
    FREE_SHIPPING_THRESHOLD = 50.00  # Livraison gratuite à partir de ce montant
    
    # ====================
    # TAXES
    # ====================
    VAT_RATE = 0.20  # 20% de TVA
    
    # ====================
    # SESSION
    # ====================
    PERMANENT_SESSION_LIFETIME = 3600  # 1 heure en secondes
    SESSION_COOKIE_SECURE = False  # Mettre à True en production avec HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # ====================
    # EMAIL (configuration basique)
    # ====================
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@dorsey-shop.com')

    # ====================
    # SMS (Twilio)
    # ====================
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_FROM = os.environ.get('TWILIO_FROM')
    
    # ====================
    # CACHE
    # ====================
    CACHE_TYPE = 'simple'  # 'redis', 'memcached', ou 'simple' pour développement
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    
    # ====================
    # DEBUG & TEST
    # ====================
    DEBUG = os.environ.get('DEBUG', 'True').lower() in ['true', 'on', '1']
    TESTING = False

    # ====================
    # INTERNATIONALISATION
    # ====================
    BABEL_DEFAULT_LOCALE = os.environ.get('BABEL_DEFAULT_LOCALE', 'fr')
    BABEL_SUPPORTED_LOCALES = ['fr', 'en', 'ar']
    BABEL_TRANSLATION_DIRECTORIES = os.environ.get('BABEL_TRANSLATION_DIRECTORIES', 'translations')
    
    # ====================
    # LOGGING
    # ====================
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    
    # ====================
    # API KEYS (pour évolutivité)
    # ====================
    STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
    STRIPE_CURRENCY = os.environ.get('STRIPE_CURRENCY', 'xaf')
    PUBLIC_BASE_URL = os.environ.get('PUBLIC_BASE_URL', '')
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
    
    # ====================
    # CATÉGORIES PAR DÉFAUT
    # ====================
    DEFAULT_CATEGORIES = [
        'Hommes',
        'Femmes',
        'Chaussures',
        'Chapeaux',
        'Accessoires',
        'Nouveautés',
        'Promotions'
    ]
    
    # ====================
    # TAILLES DISPONIBLES
    # ====================
    AVAILABLE_SIZES = {
        'vetements': ['XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL'],
        'chaussures': ['36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46'],
        'chapeaux': ['S', 'M', 'L', 'XL'],
        'unisex': ['Unique']
    }
    
    # ====================
    # COULEURS DISPONIBLES
    # ====================
    AVAILABLE_COLORS = [
        'Noir', 'Blanc', 'Gris', 'Bleu', 'Rouge', 'Vert', 'Jaune', 
        'Rose', 'Violet', 'Marron', 'Beige', 'Orange', 'Multicolor'
    ]
    
    # ====================
    # MARQUES DISPONIBLES
    # ====================
    AVAILABLE_BRANDS = [
        'DORSEY',
        'Nike',
        'Adidas',
        'Zara',
        'H&M',
        'Levi\'s',
        'Pull&Bear',
        'Bershka',
        'Stradivarius',
        'Other'
    ]


class DevelopmentConfig(Config):
    """
    Configuration pour le développement
    """
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Affiche les requêtes SQL


class TestingConfig(Config):
    """
    Configuration pour les tests
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """
    Configuration pour la production
    """
    DEBUG = False
    SQLALCHEMY_ECHO = False
    
    # Sécurité renforcée en production
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    
    # Base de données (hérite de DATABASE_URL ou fallback SQLite)
    SQLALCHEMY_DATABASE_URI = _get_database_url()
    
    # Cache Redis en production
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')


# Dictionnaire des configurations disponibles
config_dict = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config_class(config_name=None):
    """
    Retourne la classe de configuration en fonction du nom
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    return config_dict.get(config_name, config_dict['default'])


# Configuration par défaut
app_config = get_config_class()
