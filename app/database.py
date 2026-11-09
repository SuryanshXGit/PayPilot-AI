import json
import sqlite3
from pathlib import Path

from flask import g, current_app
from app.data.seed_data import INITIAL_PRODUCTS, INITIAL_BILLS


class PostgresAdapter:
    """Small compatibility layer for existing SQLite-style queries."""

    def __init__(self, connection):
        self.connection = connection

    def execute(self, sql, params=()):
        sql = sql.replace("?", "%s")
        return self.connection.execute(sql, params)

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()


def _connect_database():
    database_url = current_app.config.get("DATABASE_URL")

    if database_url:
        import psycopg
        from psycopg.rows import dict_row

        connection = psycopg.connect(
            database_url,
            row_factory=dict_row,
            connect_timeout=10
        )
        return PostgresAdapter(connection)

    db_path = current_app.config["DATABASE_PATH"]
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def get_db():
    if "db" not in g:
        g.db = _connect_database()
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def _execute_schema(connection, schema_sql):
    for statement in schema_sql.split(";"):
        statement = statement.strip()
        if statement:
            connection.execute(statement)


def _seed_products(connection):
    for prod in INITIAL_PRODUCTS:
        connection.execute("""
            INSERT INTO products (
                id, name, category, brand, price, original_price,
                description, specs, features, reliability_score,
                warranty_months, delivery_days, data_source,
                data_source_label, stock_quantity, image_url, price_history
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                category = excluded.category,
                brand = excluded.brand,
                price = excluded.price,
                original_price = excluded.original_price,
                description = excluded.description,
                specs = excluded.specs,
                features = excluded.features,
                reliability_score = excluded.reliability_score,
                warranty_months = excluded.warranty_months,
                delivery_days = excluded.delivery_days,
                data_source = excluded.data_source,
                data_source_label = excluded.data_source_label,
                stock_quantity = excluded.stock_quantity,
                image_url = excluded.image_url,
                price_history = excluded.price_history
        """, (
            prod["id"], prod["name"], prod["category"], prod["brand"],
            prod["price"], prod.get("original_price"),
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


def _seed_bills(connection):
    for bill in INITIAL_BILLS:
        connection.execute("""
            INSERT INTO bills (
                id, title, amount, due_date, category,
                recurring, is_paid, notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title = excluded.title,
                amount = excluded.amount,
                due_date = excluded.due_date,
                category = excluded.category,
                recurring = excluded.recurring,
                is_paid = excluded.is_paid,
                notes = excluded.notes
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


def init_db(db_path=None, force=False):
    database_url = current_app.config.get("DATABASE_URL")

    if database_url and db_path is None:
        connection = _connect_database()
    else:
        path = db_path or current_app.config["DATABASE_PATH"]
        connection = sqlite3.connect(path)
        connection.row_factory = sqlite3.Row

    try:
        schema_path = Path(__file__).parent / "data" / "schema.sql"

        with open(schema_path, "r", encoding="utf-8") as file:
            schema_sql = file.read()

        if force:
            connection.execute("DROP TABLE IF EXISTS locked_orders")
            connection.execute("DROP TABLE IF EXISTS bills")
            connection.execute("DROP TABLE IF EXISTS products")

        _execute_schema(connection, schema_sql)

        # These columns are already in the current schema.
        # IF NOT EXISTS also supports older database installations.
        is_postgres = bool(database_url and db_path is None)

        if is_postgres:
            connection.execute(
                "ALTER TABLE locked_orders ADD COLUMN IF NOT EXISTS approval_url TEXT"
            )
            connection.execute(
                "ALTER TABLE locked_orders ADD COLUMN IF NOT EXISTS error_message TEXT"
            )
        else:
            for column in ("approval_url TEXT", "error_message TEXT"):
                try:
                    connection.execute(
                        f"ALTER TABLE locked_orders ADD COLUMN {column}"
                    )
                except sqlite3.OperationalError:
                    pass

        product_count = connection.execute(
            "SELECT COUNT(*) AS count FROM products"
        ).fetchone()["count"]

        if product_count == 0 or force:
            _seed_products(connection)

        bill_count = connection.execute(
            "SELECT COUNT(*) AS count FROM bills"
        ).fetchone()["count"]

        if bill_count == 0 or force:
            _seed_bills(connection)

        connection.commit()

    except Exception:
        connection.close()
        raise

    connection.close()