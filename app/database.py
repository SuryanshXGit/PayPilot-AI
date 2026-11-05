import sqlite3
import json
from flask import g, current_app
from pathlib import Path
from app.data.seed_data import INITIAL_PRODUCTS, INITIAL_BILLS


def get_db():
    """Get database connection for current request context."""
    if 'db' not in g:
        db_path = current_app.config['DATABASE_PATH']
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    """Close database connection at end of request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db(db_path=None, force=False):
    """
    Initialize database tables and seed with verified catalog & bill data.
    If force is True, tables are dropped and re-created.
    """
    if db_path is None:
        db_path = current_app.config['DATABASE_PATH']

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Load and execute schema
    schema_path = Path(__file__).parent / "data" / "schema.sql"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    if force:
        cursor.executescript("""
            DROP TABLE IF EXISTS locked_orders;
            DROP TABLE IF EXISTS bills;
            DROP TABLE IF EXISTS products;
        """)

    cursor.executescript(schema_sql)

    # Safe schema migration for locked_orders columns if updating existing DB
    for col in ("approval_url TEXT", "error_message TEXT"):
        try:
            cursor.execute(f"ALTER TABLE locked_orders ADD COLUMN {col}")
        except sqlite3.OperationalError:
            pass

    # Check if products already exist
    cursor.execute("SELECT COUNT(*) as count FROM products")
    product_count = cursor.fetchone()["count"]

    if product_count == 0 or force:
        # Seed products
        for prod in INITIAL_PRODUCTS:
            cursor.execute("""
                INSERT OR REPLACE INTO products (
                    id, name, category, brand, price, original_price,
                    description, specs, features, reliability_score,
                    warranty_months, delivery_days, data_source,
                    data_source_label, stock_quantity, image_url, price_history
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                prod["id"],
                prod["name"],
                prod["category"],
                prod["brand"],
                prod["price"],
                prod.get("original_price"),
                prod.get("description", ""),
                json.dumps(prod.get("specs", {})),
                json.dumps(prod.get("features", [])),
                prod["reliability_score"],
                prod.get("warranty_months", 12),
                prod.get("delivery_days", 2),
                prod["data_source"],
                prod["data_source_label"],
                prod.get("stock_quantity", 0),
                prod.get("image_url", ""),
                json.dumps(prod.get("price_history", []))
            ))

    # Check if bills already exist
    cursor.execute("SELECT COUNT(*) as count FROM bills")
    bill_count = cursor.fetchone()["count"]

    if bill_count == 0 or force:
        for bill in INITIAL_BILLS:
            cursor.execute("""
                INSERT OR REPLACE INTO bills (
                    id, title, amount, due_date, category, recurring, is_paid, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                bill["id"],
                bill["title"],
                bill["amount"],
                bill["due_date"],
                bill["category"],
                1 if bill.get("recurring") else 0,
                1 if bill.get("is_paid") else 0,
                bill.get("notes", "")
            ))

    conn.commit()
    conn.close()
