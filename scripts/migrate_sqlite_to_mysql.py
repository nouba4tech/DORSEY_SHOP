import os
import sys
from sqlalchemy import create_engine, select, text, func

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


def _truthy(value):
    if value is None:
        return False
    return str(value).strip().lower() in {'1', 'true', 'yes', 'on'}


def _get_sqlite_url():
    sqlite_url = os.environ.get('SQLITE_URL')
    if sqlite_url:
        return sqlite_url
    sqlite_path = os.environ.get('SQLITE_PATH') or os.path.join(BASE_DIR, 'instance', 'dorsey_shop.db')
    return f"sqlite:///{sqlite_path}"


def _get_mysql_url():
    from config import _get_database_url
    url = _get_database_url()
    if url.startswith('sqlite:///'):
        return None
    return url


def _get_tables(metadata):
    preferred_order = [
        'users',
        'newsletter_subscribers',
        'categories',
        'products',
        'cart_items',
        'orders',
        'order_items',
        'site_settings',
    ]

    tables = []
    for name in preferred_order:
        table = metadata.tables.get(name)
        if table is not None:
            tables.append(table)

    # Add any remaining tables not in preferred_order
    for table in metadata.sorted_tables:
        if table not in tables:
            tables.append(table)
    return tables


def main():
    mysql_url = _get_mysql_url()
    if not mysql_url:
        print("Erreur: MySQL n'est pas configuré. Définis DATABASE_URL ou MYSQL_*.", file=sys.stderr)
        sys.exit(1)

    sqlite_url = _get_sqlite_url()
    force = _truthy(os.environ.get('MIGRATE_FORCE'))

    print(f"Source SQLite: {sqlite_url}")
    print(f"Destination MySQL: {mysql_url}")

    sqlite_engine = create_engine(sqlite_url, future=True)
    mysql_engine = create_engine(mysql_url, future=True, pool_pre_ping=True)

    # Charger les modèles pour récupérer la metadata
    from app.extensions import db
    import app.models  # noqa: F401

    db.metadata.create_all(bind=mysql_engine)
    tables = _get_tables(db.metadata)

    with sqlite_engine.connect() as src_conn, mysql_engine.begin() as dst_conn:
        dst_conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))

        existing = []
        for table in tables:
            count = dst_conn.execute(select(func.count()).select_from(table)).scalar()
            if count and count > 0:
                existing.append((table.name, count))

        if existing and not force:
            dst_conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))
            print("Erreur: la base MySQL n'est pas vide.", file=sys.stderr)
            for name, count in existing:
                print(f"- {name}: {count} lignes", file=sys.stderr)
            print("Pour forcer, relance avec MIGRATE_FORCE=1", file=sys.stderr)
            sys.exit(1)

        if existing and force:
            for table in reversed(tables):
                dst_conn.execute(table.delete())

        for table in tables:
            rows = src_conn.execute(select(table)).mappings().fetchall()
            if not rows:
                continue
            dst_conn.execute(table.insert(), rows)
            print(f"Copié {len(rows)} lignes -> {table.name}")

        dst_conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))

    print("Migration terminée.")


if __name__ == '__main__':
    main()
