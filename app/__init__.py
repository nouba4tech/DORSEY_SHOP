"""
Factory d'application Flask pour DORSEY-SHOP
"""
from flask import Flask, session, g
import os

from app.extensions import csrf, db, login_manager
from app.extensions import babel

def create_app(config_class='config.Config'):
    """
    Factory pour créer l'application Flask
    """
    # Créer l'application
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # Charger la configuration
    app.config.from_object(config_class)
    
    # S'assurer que le dossier d'upload existe (best-effort : le système de
    # fichiers est en lecture seule sur les plateformes serverless comme Vercel)
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    except OSError:
        import tempfile
        app.config['UPLOAD_FOLDER'] = os.path.join(tempfile.gettempdir(), 'uploads')
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialiser les extensions avec l'application
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    babel.init_app(app)
    
    # Register the locale selector with Babel
    from app.i18n import get_lang
    if hasattr(babel, 'localeselector'):
        babel.localeselector(get_lang)

    # Ensure the current locale is resolved before handling the request
    @app.before_request
    def set_locale():
        # store resolved language on `g` so templates and code can access it
        g.lang = get_lang()
    
    # Injecter les fonctions de traduction dans Jinja2 globals
    try:
        from flask_babel import gettext, ngettext
        app.jinja_env.globals.update({
            '_': gettext,
            'ngettext': ngettext,
        })
    except Exception:
        # Fallback si Flask-Babel n'est pas disponible
        def dummy_gettext(msg):
            return msg
        def dummy_ngettext(singular, plural, n):
            return plural if n != 1 else singular
        app.jinja_env.globals.update({
            '_': dummy_gettext,
            'ngettext': dummy_ngettext,
        })
    
    # Configurer Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
    login_manager.login_message_category = 'info'
    
    # Enregistrer les blueprints
    register_blueprints(app)
    
    # Créer les contextes pour les templates
    @app.context_processor
    def inject_shop_info():
        """Injecter les informations de la boutique dans tous les templates"""
        from config import Config
        from app.i18n import get_lang, t, LANGUAGES
        cart = session.get('cart', {})
        cart_count = 0
        if isinstance(cart, dict):
            for item in cart.values():
                if isinstance(item, dict):
                    cart_count += int(item.get('quantity', 0) or 0)

        return dict(
            shop_name=Config.SHOP_NAME,
            shop_slogan=Config.SHOP_SLOGAN,
            shop_email=Config.SHOP_EMAIL,
            shop_phone=Config.SHOP_PHONE,
            shop_address=Config.SHOP_ADDRESS,
            shop_city=Config.SHOP_CITY,
            shop_country=Config.SHOP_COUNTRY,
            cart_count=cart_count,
            t=t,
            current_lang=get_lang(),
            languages=LANGUAGES,
            lang_badges={'fr': 'FR', 'en': 'EN', 'ar': 'AR'},
            lang_flags={'fr': '🇫🇷', 'en': '🇬🇧', 'ar': '🇸🇦'},
        )
    
    @app.context_processor
    def utility_processor():
        """Fonctions utilitaires pour les templates"""
        from app.i18n import t

        def format_price(price):
            """Formater un prix en FCFA (XAF)"""
            amount = float(price or 0)
            return f"{amount:,.0f}".replace(',', ' ') + " FCFA"

        def order_status_label(status):
            status = (status or '').lower()
            labels = {
                'pending': t('En attente'),
                'processing': t('En préparation'),
                'shipped': t('Expédiée'),
                'delivered': t('Livrée'),
                'cancelled': t('Annulée'),
                'refunded': t('Remboursée'),
            }
            return labels.get(status, status or '-')

        def payment_status_label(status):
            status = (status or '').lower()
            labels = {
                'unpaid': t('Non payé'),
                'paid': t('Payé'),
                'partially_paid': t('Partiellement payé'),
                'refunded': t('Remboursé'),
            }
            return labels.get(status, status or '-')

        def order_status_badge(status):
            status = (status or '').lower()
            classes = {
                'pending': 'badge-warning',
                'processing': 'badge-info',
                'shipped': 'badge-info',
                'delivered': 'badge-success',
                'cancelled': 'badge-danger',
                'refunded': 'badge-neutral',
            }
            return classes.get(status, '')

        def payment_status_badge(status):
            status = (status or '').lower()
            classes = {
                'unpaid': 'badge-warning',
                'paid': 'badge-success',
                'partially_paid': 'badge-warning',
                'refunded': 'badge-neutral',
            }
            return classes.get(status, '')

        def order_timeline(order):
            if not order:
                return []

            steps = [
                {'label': t('Commande reçue'), 'date': order.created_at, 'done': True},
            ]

            status = (order.status or '').lower()
            payment = (order.payment_status or '').lower()

            if status in {'cancelled', 'refunded'}:
                terminal_label = t('Annulée') if status == 'cancelled' else t('Remboursée')
                steps.append({'label': terminal_label, 'date': order.updated_at, 'done': True})
                return steps

            steps.append({
                'label': t('Paiement confirmé') if payment == 'paid' else t('Paiement en attente'),
                'date': order.paid_at if payment == 'paid' else None,
                'done': payment == 'paid',
            })
            steps.append({
                'label': t('Préparation'),
                'date': order.updated_at if status in {'processing', 'shipped', 'delivered'} else None,
                'done': status in {'processing', 'shipped', 'delivered'},
            })
            steps.append({
                'label': t('Expédiée'),
                'date': order.shipped_at,
                'done': status in {'shipped', 'delivered'},
            })
            steps.append({
                'label': t('Livrée'),
                'date': order.delivered_at,
                'done': status == 'delivered',
            })

            return steps
        
        return dict(
            format_price=format_price,
            order_status_label=order_status_label,
            payment_status_label=payment_status_label,
            order_status_badge=order_status_badge,
            payment_status_badge=payment_status_badge,
            order_timeline=order_timeline,
        )
    
    return app

def register_blueprints(app):
    """Enregistrer tous les blueprints"""
    # Importer les blueprints ici pour éviter les imports circulaires
    from app.routes.main import bp as main_bp
    from app.routes.auth import bp as auth_bp
    from app.routes.products import bp as products_bp
    from app.routes.cart import bp as cart_bp
    from app.routes.admin import bp as admin_bp
    
    # Enregistrer les blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(cart_bp, url_prefix='/cart')
    app.register_blueprint(admin_bp, url_prefix='/admin')
