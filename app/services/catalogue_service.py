import json
from typing import List, Optional, Dict, Any
from app.database import get_db
from app.models import Product


class CatalogueService:
    @staticmethod
    def get_all_products(
        category: Optional[str] = None,
        search: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        sort_by: Optional[str] = None,
        in_stock_only: bool = False
    ) -> List[Product]:
        """
        Query catalogue products with flexible filters and sorting.
        Guarantees verified prices directly from the trusted database.
        """
        db = get_db()
        query = "SELECT * FROM products WHERE 1=1"
        params = []

        if category:
            query += " AND category = ?"
            params.append(category)

        if search:
            query += " AND (name LIKE ? OR description LIKE ? OR brand LIKE ?)"
            term = f"%{search}%"
            params.extend([term, term, term])

        if min_price is not None:
            query += " AND price >= ?"
            params.append(min_price)

        if max_price is not None:
            query += " AND price <= ?"
            params.append(max_price)

        if in_stock_only:
            query += " AND stock_quantity > 0"

        # Sorting logic
        if sort_by == "price_asc":
            query += " ORDER BY price ASC"
        elif sort_by == "price_desc":
            query += " ORDER BY price DESC"
        elif sort_by == "reliability_desc":
            query += " ORDER BY reliability_score DESC, price ASC"
        else:
            query += " ORDER BY category ASC, price ASC"

        cursor = db.execute(query, params)
        rows = cursor.fetchall()
        return [Product.from_row(row) for row in rows]

    @staticmethod
    def get_product_by_id(product_id: str) -> Optional[Product]:
        """Fetch a single verified product by its unique identifier."""
        db = get_db()
        cursor = db.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return Product.from_row(row)

    @staticmethod
    def get_products_by_ids(product_ids: List[str]) -> List[Product]:
        """Fetch a list of verified products preserving request order where possible."""
        if not product_ids:
            return []
        db = get_db()
        placeholders = ",".join("?" for _ in product_ids)
        cursor = db.execute(f"SELECT * FROM products WHERE id IN ({placeholders})", product_ids)
        rows = cursor.fetchall()
        product_map = {row["id"]: Product.from_row(row) for row in rows}
        return [product_map[pid] for pid in product_ids if pid in product_map]

    @staticmethod
    def get_categories() -> List[Dict[str, Any]]:
        """Return all distinct categories with metadata, counts, and price ranges."""
        db = get_db()
        cursor = db.execute("""
            SELECT
                category,
                COUNT(*) as count,
                MIN(price) as min_price,
                MAX(price) as max_price,
                AVG(reliability_score) as avg_reliability
            FROM products
            GROUP BY category
            ORDER BY category ASC
        """)
        rows = cursor.fetchall()
        return [
            {
                "category": row["category"],
                "display_name": row["category"].replace("_", " ").title(),
                "product_count": row["count"],
                "min_price": round(row["min_price"], 2),
                "max_price": round(row["max_price"], 2),
                "average_reliability": round(row["avg_reliability"], 2)
            }
            for row in rows
        ]

    @staticmethod
    def get_price_history(product_id: str) -> Optional[Dict[str, Any]]:
        """
        Get price trend history for a product.
        Complies with hackathon guardrail: clearly marks simulated/sample history.
        """
        product = CatalogueService.get_product_by_id(product_id)
        if not product:
            return None

        return {
            "product_id": product.id,
            "product_name": product.name,
            "current_trusted_price": product.price,
            "original_price": product.original_price,
            "history_data_source": "simulated_honey_trend",
            "disclosure": "Price trends are simulated sample movements for demonstration; not an active Honey API feed.",
            "history_points": product.price_history
        }
