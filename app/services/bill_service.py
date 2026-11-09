import uuid
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from app.database import get_db
from app.models import Bill


class BillService:
    """
    Proactive Financial Health Monitoring Service.
    Tracks user bill commitments and computes true disposable shopping capacity.
    """

    # Reference demo date: 2026-11-02 (matches hackathon demo period)
    DEFAULT_REFERENCE_DATE = date(2026, 11, 2)

    @staticmethod
    def get_reference_date(custom_date: Optional[str] = None) -> date:
        if custom_date:
         return datetime.strptime(custom_date, "%Y-%m-%d").date()

        return BillService.DEFAULT_REFERENCE_DATE
    @staticmethod
    def get_all_bills(
        due_within_days: Optional[int] = None,
        is_paid: Optional[bool] = None,
        reference_date_str: Optional[str] = None
    ) -> List[Bill]:
        db = get_db()
        query = "SELECT * FROM bills WHERE 1=1"
        params = []

        if is_paid is not None:
            query += " AND is_paid = ?"
            params.append(1 if is_paid else 0)

        query += " ORDER BY due_date ASC"
        cursor = db.execute(query, params)
        rows = cursor.fetchall()
        bills = [Bill.from_row(row) for row in rows]

        if due_within_days is not None:
            ref_date = BillService.get_reference_date(reference_date_str)
            filtered = []
            for b in bills:
                due = datetime.strptime(b.due_date, "%Y-%m-%d").date()
                diff_days = (due - ref_date).days
                # Due between today (0) and due_within_days
                if 0 <= diff_days <= due_within_days:
                    filtered.append(b)
            return filtered

        return bills

    @staticmethod
    def get_bill_by_id(bill_id: str) -> Optional[Bill]:
        db = get_db()
        cursor = db.execute("SELECT * FROM bills WHERE id = ?", (bill_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return Bill.from_row(row)

    @staticmethod
    def create_bill(data: Dict[str, Any]) -> Bill:
        db = get_db()
        bill_id = data.get("id") or f"bill-{uuid.uuid4().hex[:8]}"
        title = data["title"]
        amount = round(float(data["amount"]), 2)
        due_date = data["due_date"]
        category = data.get("category", "general")
        recurring = 1 if data.get("recurring", False) else 0
        is_paid = 1 if data.get("is_paid", False) else 0
        notes = data.get("notes", "")

        db.execute("""
            INSERT INTO bills (id, title, amount, due_date, category, recurring, is_paid, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (bill_id, title, amount, due_date, category, recurring, is_paid, notes))
        db.commit()

        return BillService.get_bill_by_id(bill_id)

    @staticmethod
    def update_bill(bill_id: str, data: Dict[str, Any]) -> Optional[Bill]:
        db = get_db()
        existing = BillService.get_bill_by_id(bill_id)
        if not existing:
            return None

        title = data.get("title", existing.title)
        amount = round(float(data.get("amount", existing.amount)), 2)
        due_date = data.get("due_date", existing.due_date)
        category = data.get("category", existing.category)
        recurring = 1 if data.get("recurring", existing.recurring) else 0
        is_paid = 1 if data.get("is_paid", existing.is_paid) else 0
        notes = data.get("notes", existing.notes)

        db.execute("""
            UPDATE bills
            SET title = ?, amount = ?, due_date = ?, category = ?,
                recurring = ?, is_paid = ?, notes = ?
            WHERE id = ?
        """, (title, amount, due_date, category, recurring, is_paid, notes, bill_id))
        db.commit()

        return BillService.get_bill_by_id(bill_id)

    @staticmethod
    def delete_bill(bill_id: str) -> bool:
        db = get_db()
        cursor = db.execute("DELETE FROM bills WHERE id = ?", (bill_id,))
        db.commit()
        return cursor.rowcount > 0

    @staticmethod
    def get_financial_health_summary(
        stated_shopping_budget: Optional[float] = None,
        days_window: int = 7,
        reference_date_str: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculates upcoming bills within 7 days and deterministically compares
        with the user's intended shopping budget.
        """
        ref_date = BillService.get_reference_date(reference_date_str)
        all_unpaid = BillService.get_all_bills(is_paid=False)

        upcoming_bills = []
        upcoming_bills_total = 0.0

        for b in all_unpaid:
            due = datetime.strptime(b.due_date, "%Y-%m-%d").date()
            days_left = (due - ref_date).days
            if 0 <= days_left <= days_window:
                upcoming_bills.append({
                    "id": b.id,
                    "title": b.title,
                    "amount": b.amount,
                    "due_date": b.due_date,
                    "days_remaining": days_left,
                    "category": b.category,
                    "recurring": b.recurring
                })
                upcoming_bills_total += b.amount

        upcoming_bills_total = round(upcoming_bills_total, 2)
        total_unpaid_all = round(sum(b.amount for b in all_unpaid), 2)

        summary: Dict[str, Any] = {
            "reference_date": ref_date.strftime("%Y-%m-%d"),
            "days_window": days_window,
            "total_unpaid_bills": total_unpaid_all,
            "upcoming_bills_total": upcoming_bills_total,
            "upcoming_bills_count": len(upcoming_bills),
            "upcoming_bills": upcoming_bills,
            "disclosure": "Deterministic calculation using entered bill records. Does not connect to live bank accounts."
        }

        if stated_shopping_budget is not None:
            budget = round(float(stated_shopping_budget), 2)
            disposable = round(max(0.0, budget - upcoming_bills_total), 2)
            deficit = round(abs(budget - upcoming_bills_total), 2) if upcoming_bills_total > budget else 0.0

            summary["disposable_shopping_budget_after_bills"] = disposable
            summary["shopping_budget_analysis"] = {
                "stated_shopping_budget": budget,
                "upcoming_bills_deduction": upcoming_bills_total,
                "disposable_shopping_budget_after_bills": disposable,
                "is_budget_sufficient_for_bills": upcoming_bills_total <= budget,
                "deficit": deficit,
                "advice": (
                    f"You have ${upcoming_bills_total:.2f} in bills due in the next {days_window} days. "
                    f"Your recommended safe shopping ceiling is ${disposable:.2f}."
                )
            }

        return summary
