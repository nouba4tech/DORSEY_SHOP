
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import db
from app.i18n import t
from app.forms.auth import LoginForm, RegisterForm
from app.models import Order, OrderItem, User


bp = Blueprint('auth', __name__)


@bp.get('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    return render_template('auth/login.html', form=form)


@bp.post('/login')
def login_submit():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if not form.validate_on_submit():
        return render_template('auth/login.html', form=form), 400

    user = User.query.filter_by(email=form.email.data.lower()).first()
    if not user or not user.check_password(form.password.data):
        flash(t('Identifiants invalides.'), 'danger')
        return render_template('auth/login.html', form=form), 401

    if not user.is_active:
        flash(t('Compte désactivé.'), 'danger')
        return render_template('auth/login.html', form=form), 403

    login_user(user, remember=form.remember_me.data)
    next_url = request.args.get('next')
    return redirect(next_url or url_for('main.index'))


@bp.get('/register')
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegisterForm()
    return render_template('auth/register.html', form=form)


@bp.post('/register')
def register_submit():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegisterForm()
    if not form.validate_on_submit():
        return render_template('auth/register.html', form=form), 400

    email = form.email.data.lower()
    if User.query.filter_by(email=email).first() or User.query.filter_by(username=form.username.data).first():
        flash(t('Utilisateur déjà existant.'), 'danger')
        return render_template('auth/register.html', form=form), 409

    user = User(username=form.username.data, email=email)
    user.set_password(form.password.data)
    db.session.add(user)
    db.session.commit()

    login_user(user)
    flash(t('Bienvenue ! Compte créé avec succès.'), 'success')
    return redirect(url_for('main.index'))


@bp.post('/logout')
@login_required
def logout():
    logout_user()
    flash(t('Déconnecté.'), 'info')
    return redirect(url_for('main.index'))


@bp.get('/profile')
@login_required
def profile():
    orders = current_user.orders.order_by(Order.created_at.desc()).limit(20).all() if hasattr(current_user, 'orders') else []
    return render_template('auth/profile.html', user=current_user, orders=orders)


@bp.get('/orders/<order_number>')
@login_required
def order_detail(order_number: str):
    order = Order.query.filter_by(order_number=order_number, user_id=current_user.id).first_or_404()
    items = order.items.order_by(OrderItem.id.asc()).all() if hasattr(order, 'items') else []
    return render_template('auth/order_detail.html', order=order, items=items)


@bp.get('/orders/<order_number>/invoice')
@login_required
def order_invoice(order_number: str):
    order = Order.query.filter_by(order_number=order_number, user_id=current_user.id).first_or_404()
    items = order.items.order_by(OrderItem.id.asc()).all() if hasattr(order, 'items') else []
    return render_template('orders/invoice.html', order=order, items=items)

