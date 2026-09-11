"""
Modèles de données pour DORSEY-SHOP
Optimisé pour SQLite et DB Browser
"""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager

class User(UserMixin, db.Model):
    """Modèle utilisateur"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    postal_code = db.Column(db.String(10))
    country = db.Column(db.String(100), default='France')
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    cart_items = db.relationship('CartItem', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hasher le mot de passe"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Vérifier le mot de passe"""
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        """Retourner le nom complet"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def __repr__(self):
        return f'<User {self.username}>'


class NewsletterSubscriber(db.Model):
    """Modèle inscrit newsletter"""
    __tablename__ = 'newsletter_subscribers'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    source = db.Column(db.String(50))
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(200))
    subscribed_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    unsubscribed_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<NewsletterSubscriber {self.email}>'

class Category(db.Model):
    """Modèle catégorie"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    slug = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    image = db.Column(db.String(200))
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    parent = db.relationship('Category', remote_side=[id], backref='subcategories')
    products = db.relationship('Product', backref='category', lazy='dynamic', cascade='all, delete-orphan')
    
    def product_count(self):
        """Compter les produits actifs dans cette catégorie"""
        return self.products.filter_by(is_active=True).count()
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Product(db.Model):
    """Modèle produit"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    short_description = db.Column(db.String(200))
    price = db.Column(db.Float, nullable=False)
    compare_price = db.Column(db.Float)  # Prix de comparaison (barré)
    cost_price = db.Column(db.Float)  # Prix coûtant
    quantity = db.Column(db.Integer, default=0)
    low_stock_threshold = db.Column(db.Integer, default=5)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False, index=True)
    brand = db.Column(db.String(50), index=True)
    
    # Images
    main_image = db.Column(db.String(200))
    images = db.Column(db.Text)  # JSON sérialisé comme texte pour SQLite
    
    # Caractéristiques
    sizes = db.Column(db.Text)  # JSON: ["S", "M", "L"]
    colors = db.Column(db.Text)  # JSON: ["Rouge", "Bleu"]
    material = db.Column(db.String(100))
    weight = db.Column(db.Float)  # Poids en kg
    dimensions = db.Column(db.String(50))  # "10x20x30 cm"
    
    # Localisation
    location_city = db.Column(db.String(100), default="N'Djamena")
    location_country = db.Column(db.String(100), default="Tchad")
    
    # SEO
    meta_title = db.Column(db.String(100))
    meta_description = db.Column(db.String(200))
    meta_keywords = db.Column(db.String(200))
    
    # Statut
    is_active = db.Column(db.Boolean, default=True, index=True)
    is_featured = db.Column(db.Boolean, default=False, index=True)
    is_on_sale = db.Column(db.Boolean, default=False, index=True)
    sale_price = db.Column(db.Float)
    sale_start = db.Column(db.DateTime)
    sale_end = db.Column(db.DateTime)
    
    # Statistiques
    views = db.Column(db.Integer, default=0)
    sales_count = db.Column(db.Integer, default=0)
    
    # Dates
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    cart_items = db.relationship('CartItem', backref='product', lazy='dynamic', cascade='all, delete-orphan')
    order_items = db.relationship('OrderItem', backref='product', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_stock_status(self):
        """Retourner le statut du stock"""
        quantity = self.quantity if self.quantity is not None else 0
        threshold = self.low_stock_threshold if self.low_stock_threshold is not None else 5

        if quantity <= 0:
            return 'out_of_stock'
        elif quantity <= threshold:
            return 'low_stock'
        else:
            return 'in_stock'
    
    def get_current_price(self):
        """Retourner le prix actuel (en promotion ou prix normal)"""
        if self.is_on_sale and self.sale_price:
            return self.sale_price
        return self.price
    
    def get_discount_percentage(self):
        """Calculer le pourcentage de réduction"""
        if self.is_on_sale and self.sale_price and self.compare_price:
            discount = ((self.compare_price - self.sale_price) / self.compare_price) * 100
            return round(discount, 0)
        return 0
    
    def __repr__(self):
        return f'<Product {self.name}>'

class CartItem(db.Model):
    """Modèle article du panier"""
    __tablename__ = 'cart_items'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    size = db.Column(db.String(10))
    color = db.Column(db.String(20))
    price = db.Column(db.Float)  # Prix au moment de l'ajout
    added_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def get_total(self):
        """Calculer le total pour cet article"""
        return self.price * self.quantity if self.price else 0
    
    def __repr__(self):
        return f'<CartItem {self.id}>'

class Order(db.Model):
    """Modèle commande"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Montants
    subtotal = db.Column(db.Float, nullable=False)  # Total HT
    shipping_cost = db.Column(db.Float, default=0)
    tax_amount = db.Column(db.Float, default=0)
    discount_amount = db.Column(db.Float, default=0)
    total_amount = db.Column(db.Float, nullable=False)  # Total TTC
    
    # Adresses
    shipping_full_name = db.Column(db.String(200))
    shipping_address = db.Column(db.Text)
    shipping_city = db.Column(db.String(100))
    shipping_postal_code = db.Column(db.String(10))
    shipping_country = db.Column(db.String(100), default='France')
    shipping_phone = db.Column(db.String(20))
    
    billing_full_name = db.Column(db.String(200))
    billing_address = db.Column(db.Text)
    billing_city = db.Column(db.String(100))
    billing_postal_code = db.Column(db.String(10))
    billing_country = db.Column(db.String(100), default='France')
    
    # Statut
    status = db.Column(db.String(20), default='pending', index=True)  # pending, processing, shipped, delivered, cancelled, refunded
    payment_status = db.Column(db.String(20), default='unpaid', index=True)  # unpaid, paid, partially_paid, refunded
    payment_method = db.Column(db.String(50))  # cash, card, bank_transfer, etc.
    
    # Informations
    notes = db.Column(db.Text)
    tracking_number = db.Column(db.String(100))
    carrier = db.Column(db.String(50))
    
    # Dates
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    paid_at = db.Column(db.DateTime)
    shipped_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    
    # Relations
    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    
    def generate_order_number(self):
        """Générer un numéro de commande unique"""
        from datetime import datetime
        date_str = datetime.now().strftime('%Y%m%d')
        return f"DORSEY-{date_str}-{self.id:04d}"

    def restore_stock(self):
        """Restaurer les quantités des produits pour cette commande.

        Ne réalise pas de commit; le caller doit gérer la transaction.
        Retourne le nombre total d'articles restaurés.
        """
        restored = 0
        for item in self.items.all():
            try:
                product = Product.query.filter_by(id=item.product_id).first()
            except Exception:
                product = None
            if not product:
                continue
            qty = int(item.quantity or 0)
            if product.quantity is not None:
                product.quantity = int(product.quantity or 0) + qty
            product.sales_count = max(0, (product.sales_count or 0) - qty)
            restored += qty
        return restored
    
    def __repr__(self):
        return f'<Order {self.order_number}>'

class OrderItem(db.Model):
    """Modèle article de commande"""
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    
    # Détails produit au moment de la commande
    product_name = db.Column(db.String(200), nullable=False)
    product_sku = db.Column(db.String(50))
    product_price = db.Column(db.Float, nullable=False)
    
    quantity = db.Column(db.Integer, nullable=False)
    size = db.Column(db.String(10))
    color = db.Column(db.String(20))
    total_price = db.Column(db.Float, nullable=False)  # price * quantity
    
    def __repr__(self):
        return f'<OrderItem {self.id}>'

class SiteSettings(db.Model):
    """Modèle paramètres du site"""
    __tablename__ = 'site_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text)
    value_type = db.Column(db.String(20), default='string')  # string, integer, float, boolean, json
    category = db.Column(db.String(50), default='general')
    description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @classmethod
    def get_setting(cls, key, default=None):
        """Récupérer un paramètre"""
        setting = cls.query.filter_by(key=key).first()
        if setting:
            # Convertir selon le type
            if setting.value_type == 'integer':
                return int(setting.value) if setting.value else default
            elif setting.value_type == 'float':
                return float(setting.value) if setting.value else default
            elif setting.value_type == 'boolean':
                return setting.value.lower() == 'true' if setting.value else default
            elif setting.value_type == 'json':
                import json
                return json.loads(setting.value) if setting.value else default
            else:
                return setting.value or default
        return default
    
    @classmethod
    def set_setting(cls, key, value, value_type='string', category='general', description=''):
        """Définir un paramètre"""
        setting = cls.query.filter_by(key=key).first()
        
        # Convertir la valeur en string
        if value_type == 'json' and not isinstance(value, str):
            import json
            value_str = json.dumps(value)
        else:
            value_str = str(value)
        
        if setting:
            setting.value = value_str
            setting.value_type = value_type
            setting.category = category
            setting.description = description
        else:
            setting = cls(
                key=key,
                value=value_str,
                value_type=value_type,
                category=category,
                description=description
            )
            db.session.add(setting)
        
        db.session.commit()
        return setting
    
    def __repr__(self):
        return f'<SiteSetting {self.key}>'

# Configuration du login manager
@login_manager.user_loader
def load_user(user_id):
    """Charger l'utilisateur pour Flask-Login"""
    return User.query.get(int(user_id))
