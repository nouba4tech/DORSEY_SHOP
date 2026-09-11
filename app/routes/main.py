from datetime import datetime

from email_validator import EmailNotValidError, validate_email
from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for, session, abort
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.i18n import LANGUAGES, t
from app.models import Category, NewsletterSubscriber, Order, Product

bp = Blueprint('main', __name__)


@bp.get('/')
def index():
    categories = Category.query.filter_by(is_active=True).order_by(Category.display_order.asc(), Category.name.asc()).all()
    featured_products = (
        Product.query.filter_by(is_active=True)
        .order_by(Product.is_featured.desc(), Product.created_at.desc())
        .limit(8)
        .all()
    )
    showcase_products = []
    showcase_category = None
    showcase_categories = (
        Category.query.join(Product)
        .filter(Category.is_active.is_(True), Product.is_active.is_(True))
        .distinct()
        .order_by(Category.display_order.asc(), Category.name.asc())
        .all()
    )
    if showcase_categories:
        index = session.get('showcase_category_index', 0) % len(showcase_categories)
        showcase_category = showcase_categories[index]
        session['showcase_category_index'] = (index + 1) % len(showcase_categories)
        showcase_products = (
            Product.query.filter_by(is_active=True, category_id=showcase_category.id)
            .order_by(Product.is_featured.desc(), Product.created_at.desc())
            .limit(8)
            .all()
        )
    if not showcase_products:
        showcase_products = (
            Product.query.filter_by(is_active=True)
            .order_by(Product.is_featured.desc(), Product.created_at.desc())
            .limit(8)
            .all()
        )
    if len(showcase_products) < 8:
        excluded_ids = [p.id for p in showcase_products]
        filler_query = Product.query.filter(Product.is_active.is_(True))
        if excluded_ids:
            filler_query = filler_query.filter(Product.id.notin_(excluded_ids))
        filler = (
            filler_query.order_by(Product.is_featured.desc(), Product.created_at.desc())
            .limit(8 - len(showcase_products))
            .all()
        )
        showcase_products.extend(filler)

    return render_template(
        'index.html',
        categories=categories,
        featured_products=featured_products,
        showcase_category=showcase_category,
        showcase_products=showcase_products,
    )


@bp.get('/about')
def about():
    return render_template('about.html')


@bp.get('/contact')
def contact():
    return render_template('contact.html')


@bp.get('/aide')
def help_center():
    return render_template('help.html')


@bp.get('/lang/<lang>')
def set_language(lang):
    if lang not in LANGUAGES:
        abort(404)
    session['lang'] = lang
    redirect_url = request.referrer or url_for('main.index')
    response = redirect(redirect_url)
    response.set_cookie('lang', lang, max_age=60 * 60 * 24 * 365, samesite='Lax')
    return response


@bp.get('/suivi-commande')
def track_order():
    order_number = (request.args.get('order') or '').strip().upper()
    return render_template('orders/track.html', order_number=order_number, order=None)


@bp.post('/suivi-commande')
def track_order_submit():
    order_number = (request.form.get('order_number') or '').strip().upper()
    phone = (request.form.get('phone') or '').strip()

    if not order_number or not phone:
        flash(t('Merci de renseigner le numéro de commande et le téléphone.'), 'danger')
        return render_template('orders/track.html', order_number=order_number, order=None), 400

    order = Order.query.filter_by(order_number=order_number, shipping_phone=phone).first()
    if not order:
        flash(t('Commande introuvable. Vérifiez les informations.'), 'danger')
        return render_template('orders/track.html', order_number=order_number, order=None), 404

    return render_template('orders/track.html', order_number=order_number, order=order)


def _newsletter_response(message, status_code=200, state='success'):
    wants_json = (
        request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        or (request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html)
    )

    if wants_json:
        return jsonify({'status': state, 'message': message}), status_code

    redirect_url = request.referrer or url_for('main.index')
    separator = '&' if '?' in redirect_url else '?'
    return redirect(f"{redirect_url}{separator}newsletter={state}")


@bp.post('/newsletter/subscribe')
def subscribe_newsletter():
    raw_email = request.form.get('email', '').strip().lower()
    if not raw_email:
        return _newsletter_response(t("Merci de saisir une adresse email."), 400, 'invalid')

    try:
        normalized_email = validate_email(raw_email, check_deliverability=False).email.lower()
    except EmailNotValidError:
        return _newsletter_response(t("Adresse email invalide."), 400, 'invalid')

    subscriber = NewsletterSubscriber.query.filter_by(email=normalized_email).first()
    if subscriber and subscriber.is_active:
        return _newsletter_response(t("Vous êtes déjà inscrit à la newsletter."), 200, 'exists')

    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr or '')
    if ip_address and ',' in ip_address:
        ip_address = ip_address.split(',', 1)[0].strip()

    user_agent = (request.headers.get('User-Agent') or '')[:200]

    if subscriber:
        subscriber.is_active = True
        subscriber.unsubscribed_at = None
        subscriber.subscribed_at = datetime.utcnow()
        subscriber.ip_address = ip_address
        subscriber.user_agent = user_agent
    else:
        subscriber = NewsletterSubscriber(
            email=normalized_email,
            source=request.form.get('source') or 'footer',
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db.session.add(subscriber)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _newsletter_response(t("Vous êtes déjà inscrit à la newsletter."), 200, 'exists')
    except Exception:
        db.session.rollback()
        return _newsletter_response(t("Une erreur est survenue. Réessayez plus tard."), 500, 'error')

    return _newsletter_response(t("Merci ! Votre inscription est confirmée."), 201, 'success')

