import json
from dataclasses import dataclass, asdict
from datetime import datetime, date
from typing import List, Dict, Any, Optional


@dataclass
class Product:
    id: str
    name: str
    category: str
    brand: str
    price: float
    reliability_score: float
    data_source: str
    data_source_label: str
    original_price: Optional[float] = None
    description: str = ""
    specs: Dict[str, Any] = None
    features: List[str] = None
    warranty_months: int = 12
    delivery_days: int = 2
    stock_quantity: int = 0
    image_url: str = ""
    price_history: List[Dict[str, Any]] = None

    @classmethod
    def from_row(cls, row) -> "Product":
        return cls(
            id=row["id"],
            name=row["name"],
            category=row["category"],
            brand=row["brand"],
            price=float(row["price"]),
            original_price=float(row["original_price"]) if row["original_price"] is not None else None,
            description=row["description"] or "",
            specs=json.loads(row["specs"]) if row["specs"] else {},
            features=json.loads(row["features"]) if row["features"] else [],
            reliability_score=float(row["reliability_score"]),
            warranty_months=int(row["warranty_months"]),
            delivery_days=int(row["delivery_days"]),
            data_source=row["data_source"],
            data_source_label=row["data_source_label"],
            stock_quantity=int(row["stock_quantity"]),
            image_url=row["image_url"] or "",
            price_history=json.loads(row["price_history"]) if row["price_history"] else []
        )

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


@dataclass
class Bill:
    id: str
    title: str
    amount: float
    due_date: str
    category: str
    recurring: bool = False
    is_paid: bool = False
    notes: str = ""

    @classmethod
    def from_row(cls, row) -> "Bill":
        return cls(
            id=row["id"],
            title=row["title"],
            amount=float(row["amount"]),
            due_date=row["due_date"],
            category=row["category"],
            recurring=bool(row["recurring"]),
            is_paid=bool(row["is_paid"]),
            notes=row["notes"] or ""
        )

    def days_until_due(self, reference_date: Optional[date] = None) -> int:
        if reference_date is None:
            reference_date = date.today()
        due = datetime.strptime(self.due_date, "%Y-%m-%d").date()
        return (due - reference_date).days

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d
