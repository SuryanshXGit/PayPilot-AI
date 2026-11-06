from app.services.catalogue_service import CatalogueService


def test_catalogue_seed_loaded(app):
    with app.app_context():
        products = CatalogueService.get_all_products()
        assert len(products) >= 10
        # Check dorm scenario products are present
        categories = {p.category for p in products}
        assert "desk_lamp" in categories
        assert "portable_steamer" in categories
        assert "noise_cancelling_earbuds" in categories
        assert "laptop" in categories
        assert "medical_equipment" in categories


def test_catalogue_filter_by_category(app):
    with app.app_context():
        lamps = CatalogueService.get_all_products(category="desk_lamp")
        assert len(lamps) == 3
        for lamp in lamps:
            assert lamp.category == "desk_lamp"


def test_catalogue_filter_by_price_and_sort(app):
    with app.app_context():
        affordable_items = CatalogueService.get_all_products(
            max_price=35.00,
            sort_by="price_asc"
        )
        assert len(affordable_items) > 0
        prices = [p.price for p in affordable_items]
        assert prices == sorted(prices)
        assert all(p <= 35.00 for p in prices)


def test_catalogue_search(app):
    with app.app_context():
        results = CatalogueService.get_all_products(search="Anker")
        assert len(results) >= 1
        assert "Anker" in results[0].name or "Anker" in results[0].brand


def test_catalogue_data_source_labeling(app):
    """Compliance test: verifies that all products include transparent data labeling."""
    with app.app_context():
        products = CatalogueService.get_all_products()
        for p in products:
            assert p.data_source is not None
            assert len(p.data_source) > 0
            assert p.data_source_label is not None
            assert "Controlled Catalogue Price" in p.data_source_label


def test_catalogue_price_history_disclosure(app):
    """Compliance test: verifies price history is labeled as simulated."""
    with app.app_context():
        history = CatalogueService.get_price_history("buds-anker-space-a40")
        assert history is not None
        assert history["history_data_source"] == "simulated_honey_trend"
        assert "simulated" in history["disclosure"].lower()
        assert len(history["history_points"]) > 0
