
from functools import wraps

from datetime import datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.i18n import t
from app.models import Order, OrderItem, Product, User
from app.utils.notifications import send_order_shipped_notifications
from app.utils.notifications import send_order_refunded_notifications


bp = Blueprint('admin', __name__)


def admin_required(fn):
    @wraps(fn)
    @login_required
    def wrapper(*args, **kwargs):
        if not getattr(current_user, 'is_admin', False):
            abort(403)
        return fn(*args, **kwargs)

    return wrapper


@bp.get('/')
@admin_required
def dashboard():
    stats = {
        'users': User.query.count(),
        'products': Product.query.count(),
        'orders': Order.query.count(),
    }
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    return render_template('admin/dashboard.html', stats=stats, recent_orders=recent_orders)


@bp.get('/orders')
@admin_required
def orders():
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(200).all()
    return render_template('admin/orders.html', orders=recent_orders)


@bp.get('/orders/<int:order_id>')
@admin_required
def order_detail(order_id: int):
    order = Order.query.filter_by(id=order_id).first_or_404()
    return render_template('admin/order_detail.html', order=order)


@bp.get('/orders/<int:order_id>/invoice')
@admin_required
def order_invoice(order_id: int):
    order = Order.query.filter_by(id=order_id).first_or_404()
    items = order.items.order_by(OrderItem.id.asc()).all() if hasattr(order, 'items') else []
    return render_template('orders/invoice.html', order=order, items=items)


@bp.post('/orders/<int:order_id>')
@admin_required
def order_update(order_id: int):
    order = Order.query.filter_by(id=order_id).first_or_404()

    prev_status = order.status
    prev_payment = order.payment_status
    prev_tracking = order.tracking_number or ''

    status = (request.form.get('status') or '').strip().lower()
    payment_status = (request.form.get('payment_status') or '').strip().lower()
    carrier = (request.form.get('carrier') or '').strip()
    tracking_number = (request.form.get('tracking_number') or '').strip()

    if status:
        order.status = status
    if payment_status:
        order.payment_status = payment_status

    order.carrier = carrier or None
    order.tracking_number = tracking_number or None

    if order.status == 'shipped' and prev_status != 'shipped':
        order.shipped_at = datetime.utcnow()
    if order.status == 'delivered' and prev_status != 'delivered':
        order.delivered_at = datetime.utcnow()
    if order.payment_status == 'paid' and prev_payment != 'paid':
        order.paid_at = datetime.utcnow()

    db.session.commit()

    should_notify = False
    if order.status == 'shipped' and prev_status != 'shipped':
        should_notify = True
    if order.status == 'shipped' and not prev_tracking and order.tracking_number:
        should_notify = True

    if should_notify:
        send_order_shipped_notifications(order)

    flash(t('Commande mise à jour.'), 'success')
    return redirect(url_for('admin.order_detail', order_id=order.id))


@bp.post('/orders/<int:order_id>/refund')
@admin_required
def order_refund(order_id: int):
    """Marquer une commande comme remboursée et restaurer le stock."""
    order = Order.query.filter_by(id=order_id).first_or_404()
    if order.payment_status == 'refunded':
        flash(t('La commande est déjà remboursée.'), 'info')
        return redirect(url_for('admin.order_detail', order_id=order.id))

    try:
        restored = order.restore_stock()
    except Exception:
        restored = 0

    order.payment_status = 'refunded'
    order.status = 'cancelled'
    db.session.commit()
    send_order_refunded_notifications(order)

    flash(t('Commande remboursée et stock restauré.'), 'success')
    return redirect(url_for('admin.order_detail', order_id=order.id))

