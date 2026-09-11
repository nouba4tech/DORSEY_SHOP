
import json

from flask import Blueprint, current_app, render_template, request
from sqlalchemy import func, or_

from app.models import Category, Product


bp = Blueprint('products', __name__)


@bp.get('/')
def list_products():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '', type=str).strip()
    category_filter = request.args.get('category', '', type=str).strip()
    sort = request.args.get('sort', 'new', type=str).strip()

    query = Product.query.filter_by(is_active=True)

    active_category = None
    if category_filter and category_filter.lower() not in {'all', 'toute-la-boutique', 'toute_boutique'}:
        if category_filter.isdigit():
            active_category = Category.query.filter_by(id=int(category_filter), is_active=True).first()
        else:
            active_category = (
                Category.query.filter(
                    Category.is_active.is_(True),
                    (func.lower(Category.slug) == category_filter.lower())
                    | (func.lower(Category.name) == category_filter.lower())
                )
                .first()
            )
        if active_category:
            query = query.filter(Product.category_id == active_category.id)
        else:
            # If a category filter is provided but not found, return no product
            # instead of falling back to the full catalog.
            query = query.filter(Product.id == -1)

    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Product.name.ilike(like),
                Product.short_description.ilike(like),
                Product.description.ilike(like),
                Product.sku.ilike(like),
                Product.slug.ilike(like),
            )
        )

    if sort == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif sort == 'popular':
        query = query.order_by(Product.views.desc(), Product.sales_count.desc())
    else:
        query = query.order_by(Product.created_at.desc())

    per_page = current_app.config.get('PRODUCTS_PER_PAGE', 12)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    categories = Category.query.filter_by(is_active=True).order_by(Category.display_order.asc(), Category.name.asc()).all()
    return render_template(
        'products/list.html',
        categories=categories,
        active_category=active_category,
        q=q,
        sort=sort,
        pagination=pagination,
        products=pagination.items,
    )


@bp.get('/<int:product_id>')
def product_detail(product_id: int):
    product = Product.query.filter_by(id=product_id, is_active=True).first_or_404()

    product.views = (product.views or 0) + 1
    from app.extensions import db

    db.session.commit()

    sizes = []
    colors = []
    images = []
    try:
        sizes = json.loads(product.sizes) if product.sizes else []
    except Exception:
        sizes = []
    try:
        colors = json.loads(product.colors) if product.colors else []
    except Exception:
        colors = []
    try:
        images = json.loads(product.images) if product.images else []
    except Exception:
        images = []

    return render_template('products/detail.html', product=product, sizes=sizes, colors=colors, images=images)

