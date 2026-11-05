from app.services.bill_service import BillService


def test_seed_bills_loaded(app):
    with app.app_context():
        bills = BillService.get_all_bills()
        assert len(bills) == 4
        unpaid = BillService.get_all_bills(is_paid=False)
        assert len(unpaid) == 4


def test_upcoming_bills_7_days_filter(app):
    with app.app_context():
        # Demo reference date: 2026-11-02
        # Bills due within 7 days: 2026-11-05 ($45) and 2026-11-08 ($35) = $80.00
        upcoming = BillService.get_all_bills(
            due_within_days=7,
            reference_date_str="2026-11-02"
        )
        assert len(upcoming) == 2
        titles = {b.title for b in upcoming}
        assert "Campus Utility / Dorm Electric" in titles
        assert "High-Speed Dorm WiFi" in titles
        total_upcoming = sum(b.amount for b in upcoming)
        assert total_upcoming == 80.00


def test_bill_crud_operations(app):
    with app.app_context():
        # Create
        new_bill = BillService.create_bill({
            "title": "Laundry Card Reload",
            "amount": 20.00,
            "due_date": "2026-11-04",
            "category": "personal"
        })
        assert new_bill is not None
        assert new_bill.title == "Laundry Card Reload"
        assert new_bill.amount == 20.00

        # Read
        fetched = BillService.get_bill_by_id(new_bill.id)
        assert fetched.id == new_bill.id

        # Update
        updated = BillService.update_bill(new_bill.id, {"amount": 25.00, "is_paid": True})
        assert updated.amount == 25.00
        assert updated.is_paid is True

        # Delete
        deleted = BillService.delete_bill(new_bill.id)
        assert deleted is True
        assert BillService.get_bill_by_id(new_bill.id) is None


def test_financial_health_summary(app):
    with app.app_context():
        summary = BillService.get_financial_health_summary(
            stated_shopping_budget=150.00,
            days_window=7,
            reference_date_str="2026-11-02"
        )

        assert summary["upcoming_bills_total"] == 80.00
        assert summary["upcoming_bills_count"] == 2
        assert "shopping_budget_analysis" in summary
        analysis = summary["shopping_budget_analysis"]
        assert analysis["stated_shopping_budget"] == 150.00
        assert analysis["disposable_shopping_budget_after_bills"] == 70.00
        assert analysis["is_budget_sufficient_for_bills"] is True
