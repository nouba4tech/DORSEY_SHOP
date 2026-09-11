
from __future__ import annotations

from datetime import datetime

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.i18n import t
from app.forms.checkout import CheckoutForm
from app.models import Order, OrderItem, Product
from app.utils.notifications import send_order_notifications
from app.utils.payments import (
    construct_webhook_event,
    create_checkout_session,
    retrieve_checkout_session,
    stripe_is_configured,
)


bp = Blueprint('cart', __name__)


def _get_cart() -> dict:
    cart = session.get('cart')
    if not isinstance(cart, dict):
        cart = {}
    return cart


def _save_cart(cart: dict) -> None:
    session['cart'] = cart
    session.modified = True


def _cart_items():
    cart = _get_cart()
    if not cart:
        return []

    product_ids = [int(pid) for pid in cart.keys() if str(pid).isdigit()]
    products = Product.query.filter(Product.id.in_(product_ids), Product.is_active.is_(True)).all()
    products_by_id = {p.id: p for p in products}

    items = []
    for pid_str, item in cart.items():
        if not str(pid_str).isdigit():
            continue
        pid = int(pid_str)
        product = products_by_id.get(pid)
        if not product:
            continue

        qty = int(item.get('quantity', 1) or 1)
        qty = max(1, qty)
        size = (item.get('size') or '').strip() or None
        color = (item.get('color') or '').strip() or None
        unit_price = float(item.get('price') or product.get_current_price())

        items.append(
            {
                'product': product,
                'product_id': product.id,
                'quantity': qty,
                'size': size,
                'color': color,
                'unit_price': unit_price,
                'total': unit_price * qty,
            }
        )

    return items


def _apply_promo(subtotal: float, code: str):
    code = (code or '').strip().upper()
    promotions = {
        'WELCOME10': {'type': 'percent', 'value': 10.0, 'min': 30.0},
        'SUMMER20': {'type': 'percent', 'value': 20.0, 'min': 50.0},
        'FIXED15': {'type': 'fixed', 'value': 15.0, 'min': 50.0},
    }
    promo = promotions.get(code)
    if not promo:
        return 0.0, None
    if subtotal < float(promo['min']):
        return 0.0, None
    if promo['type'] == 'percent':
        return round(subtotal * (float(promo['value']) / 100.0), 2), code
    return min(float(promo['value']), subtotal), code


def _totals(subtotal: float, shipping_method: str, promo_code: str):
    vat_rate = float(current_app.config.get('VAT_RATE', 0.20))

    shipping_method = (shipping_method or 'standard').strip().lower()
    free_threshold = float(current_app.config.get('FREE_SHIPPING_THRESHOLD', 50.0))

    shipping_cost = 0.0
    if subtotal < free_threshold:
        if shipping_method == 'express':
            shipping_cost = float(current_app.config.get('SHIPPING_COST_EXPRESS', 9.90))
        else:
            shipping_cost = float(current_app.config.get('SHIPPING_COST_STANDARD', 4.90))

    discount_amount, applied_code = _apply_promo(subtotal, promo_code)
    taxable_base = max(0.0, subtotal - discount_amount)
    tax_amount = round(taxable_base * vat_rate, 2)
    total_amount = round(taxable_base + tax_amount + shipping_cost, 2)

    return {
        'subtotal': round(subtotal, 2),
        'shipping_cost': round(shipping_cost, 2),
        'discount_amount': round(discount_amount, 2),
        'tax_amount': round(tax_amount, 2),
        'total_amount': round(total_amount, 2),
        'applied_promo_code': applied_code,
        'shipping_method': shipping_method,
    }


def _localize_checkout_form(form: CheckoutForm) -> None:
    form.full_name.label.text = t('Nom complet')
    form.phone.label.text = t('Téléphone')
    form.address.label.text = t('Adresse')
    form.city.label.text = t('Ville')
    form.postal_code.label.text = t('Code postal')
    form.country.label.text = t('Pays')
    form.shipping_method.label.text = t('Mode de livraison')
    form.shipping_method.choices = [
        ('standard', t('Standard')),
        ('express', t('Express')),
    ]
    form.payment_method.label.text = t('Mode de paiement')
    form.payment_method.choices = [
        ('card', t('Carte (Stripe)')),
        ('cash', t('Paiement à la livraison')),
    ]
    form.submit.label.text = t('Confirmer la commande')


def _apply_stock_and_sales(order: Order):
    # Retourne True si l'opération réussit, False si stock insuffisant
    for item in order.items.all():
        product = Product.query.filter_by(id=item.product_id).first()
        if not product:
            continue
        qty = int(item.quantity or 0)
        if product.quantity is not None:
            if int(product.quantity) < qty:
                return False
            product.quantity = max(0, int(product.quantity) - qty)
        product.sales_count = (product.sales_count or 0) + qty
    return True


def _mark_order_paid(order: Order) -> bool:
    if order.payment_status == 'paid':
        return False
    # Essayer d'appliquer la décrémentation du stock.
    success = _apply_stock_and_sales(order)
    order.payment_status = 'paid'
    order.paid_at = datetime.utcnow()
    if not success:
        # Paiement reçu mais stock insuffisant -> mettre en attente pour intervention admin
        order.status = 'on_hold'
        return True

    order.status = 'processing'
    return True


@bp.get('/')
def view_cart():
    items = _cart_items()
    subtotal = sum(i['total'] for i in items)
    promo_code = session.get('promo_code', '')
    shipping_method = session.get('shipping_method', 'standard')
    totals = _totals(subtotal, shipping_method, promo_code)
    return render_template('cart/view.html', items=items, totals=totals)


@bp.post('/add/<int:product_id>')
def add_to_cart(product_id: int):
    product = Product.query.filter_by(id=product_id, is_active=True).first_or_404()
    quantity = request.form.get('quantity', 1, type=int)
    quantity = max(1, min(quantity, 99))
    # Respecter le stock disponible si renseigné
    if product.quantity is not None and quantity > int(product.quantity):
        quantity = int(product.quantity)
        flash(t('Quantité ajustée à la disponibilité en stock.'), 'warning')
    size = (request.form.get('size') or '').strip()
    color = (request.form.get('color') or '').strip()

    cart = _get_cart()
    key = str(product.id)
    existing = cart.get(key, {})
    existing_qty = int(existing.get('quantity', 0) or 0)

    cart[key] = {
        'quantity': min(existing_qty + quantity, 99),
        'size': size,
        'color': color,
        'price': float(product.get_current_price()),
    }
    _save_cart(cart)
    flash(t('Produit ajouté au panier.'), 'success')

    buy_now = (request.form.get('buy_now') or '').strip().lower() in {'1', 'true', 'yes', 'on'}
    if buy_now:
        if current_user.is_authenticated:
            return redirect(url_for('cart.checkout'))
        return redirect(url_for('auth.login', next=url_for('cart.checkout')))

    return redirect(request.referrer or url_for('cart.view_cart'))


@bp.post('/update/<int:product_id>')
def update_cart_item(product_id: int):
    quantity = request.form.get('quantity', 1, type=int)
    quantity = max(1, min(quantity, 99))
    # Vérifier le stock du produit avant d'appliquer
    product = Product.query.filter_by(id=product_id, is_active=True).first()
    if product and product.quantity is not None and quantity > int(product.quantity):
        quantity = int(product.quantity)
        flash(t('Quantité limitée à la disponibilité en stock.'), 'warning')

    cart = _get_cart()
    key = str(product_id)
    if key in cart:
        cart[key]['quantity'] = quantity
        _save_cart(cart)
        flash(t('Panier mis à jour.'), 'success')
    return redirect(url_for('cart.view_cart'))


@bp.post('/remove/<int:product_id>')
def remove_cart_item(product_id: int):
    cart = _get_cart()
    key = str(product_id)
    if key in cart:
        cart.pop(key, None)
        _save_cart(cart)
        flash(t('Article supprimé du panier.'), 'success')
    return redirect(url_for('cart.view_cart'))


@bp.post('/promo')
def apply_promo():
    code = (request.form.get('promo_code') or '').strip().upper()
    session['promo_code'] = code
    session.modified = True
    return redirect(url_for('cart.view_cart'))


@bp.get('/checkout')
@login_required
def checkout():
    items = _cart_items()
    if not items:
        flash(t('Votre panier est vide.'), 'info')
        return redirect(url_for('products.list_products'))

    form = CheckoutForm()
    _localize_checkout_form(form)
    if not form.full_name.data:
        form.full_name.data = current_user.get_full_name()
        form.phone.data = current_user.phone or ''
        form.address.data = current_user.address or ''
        form.city.data = current_user.city or ''
        form.postal_code.data = current_user.postal_code or ''
        form.country.data = current_user.country or 'France'

    subtotal = sum(i['total'] for i in items)
    promo_code = session.get('promo_code', '')
    totals = _totals(subtotal, form.shipping_method.data, promo_code)
    return render_template('cart/checkout.html', form=form, items=items, totals=totals)


@bp.post('/checkout')
@login_required
def checkout_submit():
    items = _cart_items()
    if not items:
        flash(t('Votre panier est vide.'), 'info')
        return redirect(url_for('products.list_products'))

    form = CheckoutForm()
    _localize_checkout_form(form)
    if not form.validate_on_submit():
        subtotal = sum(i['total'] for i in items)
        promo_code = session.get('promo_code', '')
        totals = _totals(subtotal, form.shipping_method.data, promo_code)
        return render_template('cart/checkout.html', form=form, items=items, totals=totals), 400

    subtotal = sum(i['total'] for i in items)
    promo_code = session.get('promo_code', '')
    totals = _totals(subtotal, form.shipping_method.data, promo_code)

    payment_method = form.payment_method.data
    if payment_method == 'card' and not stripe_is_configured():
        flash(t('Paiement en ligne indisponible. Veuillez choisir un autre moyen de paiement.'), 'danger')
        subtotal = sum(i['total'] for i in items)
        promo_code = session.get('promo_code', '')
        totals = _totals(subtotal, form.shipping_method.data, promo_code)
        return render_template('cart/checkout.html', form=form, items=items, totals=totals), 400

    # Vérifier que les quantités demandées sont toujours disponibles
    for it in items:
        product: Product = it['product']
        qty = int(it['quantity'])
        if product.quantity is not None and qty > int(product.quantity):
            flash(t("La quantité demandée pour le produit '%(name)s' n'est plus disponible.", name=product.name), 'danger')
            subtotal = sum(i['total'] for i in items)
            totals = _totals(subtotal, form.shipping_method.data, promo_code)
            return render_template('cart/checkout.html', form=form, items=items, totals=totals), 400

    order = Order(
        order_number='PENDING',
        user_id=current_user.id,
        subtotal=totals['subtotal'],
        shipping_cost=totals['shipping_cost'],
        tax_amount=totals['tax_amount'],
        discount_amount=totals['discount_amount'],
        total_amount=totals['total_amount'],
        shipping_full_name=form.full_name.data,
        shipping_address=form.address.data,
        shipping_city=form.city.data,
        shipping_postal_code=form.postal_code.data,
        shipping_country=form.country.data,
        shipping_phone=form.phone.data,
        billing_full_name=form.full_name.data,
        billing_address=form.address.data,
        billing_city=form.city.data,
        billing_postal_code=form.postal_code.data,
        billing_country=form.country.data,
        status='pending' if payment_method == 'card' else 'processing',
        payment_status='unpaid',
        payment_method=payment_method,
        paid_at=None,
    )
    db.session.add(order)
    db.session.flush()

    order.order_number = order.generate_order_number()

    for it in items:
        product: Product = it['product']
        qty = int(it['quantity'])

        oi = OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_name=product.name,
            product_sku=product.sku,
            product_price=float(it['unit_price']),
            quantity=qty,
            size=it['size'],
            color=it['color'],
            total_price=float(it['total']),
        )
        db.session.add(oi)

    if payment_method == 'cash':
        success = _apply_stock_and_sales(order)
        if not success:
            db.session.rollback()
            flash(t("Quantité insuffisante pour finaliser la commande. Vérifiez votre panier."), 'danger')
            return redirect(url_for('cart.checkout'))
        db.session.commit()
        _save_cart({})
        session.pop('promo_code', None)
        session.modified = True
        send_order_notifications(order)
        return redirect(url_for('cart.confirmation', order_number=order.order_number))

    db.session.commit()

    success_url = url_for('cart.stripe_success', _external=True)
    cancel_url = url_for('cart.stripe_cancel', _external=True)
    currency = current_app.config.get('STRIPE_CURRENCY', 'xaf')
    try:
        stripe_session = create_checkout_session(order, success_url, cancel_url, currency)
    except Exception:
        flash(t('Paiement en ligne indisponible. Merci de réessayer.'), 'danger')
        return redirect(url_for('cart.checkout'))
    order.notes = (order.notes or '') + f"\nstripe_session={stripe_session.id}"
    db.session.commit()
    return redirect(stripe_session.url)


@bp.get('/confirmation/<order_number>')
@login_required
def confirmation(order_number: str):
    order = Order.query.filter_by(order_number=order_number, user_id=current_user.id).first_or_404()
    return render_template('cart/confirmation.html', order=order)


@bp.get('/stripe/success')
@login_required
def stripe_success():
    session_id = (request.args.get('session_id') or '').strip()
    if not session_id:
        flash(t('Session de paiement manquante.'), 'danger')
        return redirect(url_for('cart.view_cart'))

    session_data = retrieve_checkout_session(session_id)
    if session_data.payment_status != 'paid':
        flash(t('Paiement non confirmé. Si besoin, contactez le support.'), 'danger')
        return redirect(url_for('cart.view_cart'))

    order_id = None
    if session_data.metadata:
        order_id = session_data.metadata.get('order_id')
    if not order_id:
        flash(t('Commande introuvable pour cette session.'), 'danger')
        return redirect(url_for('cart.view_cart'))

    order = Order.query.filter_by(id=int(order_id), user_id=current_user.id).first_or_404()
    if _mark_order_paid(order):
        db.session.commit()
        send_order_notifications(order)

    _save_cart({})
    session.pop('promo_code', None)
    session.modified = True

    return redirect(url_for('cart.confirmation', order_number=order.order_number))


@bp.get('/stripe/cancel')
@login_required
def stripe_cancel():
    flash(t('Paiement annulé. Votre commande est en attente.'), 'info')
    return redirect(url_for('cart.view_cart'))


@bp.post('/stripe/webhook')
def stripe_webhook():
    payload = request.data.decode('utf-8')
    sig_header = request.headers.get('Stripe-Signature', '')
    try:
        event = construct_webhook_event(payload, sig_header)
    except Exception:
        return ('', 400)

    if event['type'] == 'checkout.session.completed':
        session_obj = event['data']['object']
        metadata = session_obj.get('metadata', {})
        order_id = metadata.get('order_id')
        if order_id:
            order = Order.query.filter_by(id=int(order_id)).first()
            if order and _mark_order_paid(order):
                db.session.commit()
                send_order_notifications(order)

    # Gérer les remboursements Stripe si fournis
    if event['type'] in ('charge.refunded', 'charge.refund.updated'):
        obj = event['data'].get('object', {})
        metadata = obj.get('metadata', {}) or {}
        order_id = metadata.get('order_id')
        if order_id:
            order = Order.query.filter_by(id=int(order_id)).first()
            if order and order.payment_status != 'refunded':
                # Restaurer le stock et marquer remboursé
                try:
                    restored = order.restore_stock()
                except Exception:
                    restored = 0
                order.payment_status = 'refunded'
                order.status = 'cancelled'
                db.session.commit()
                from app.utils.notifications import send_order_refunded_notifications
                send_order_refunded_notifications(order)

    return ('', 200)

