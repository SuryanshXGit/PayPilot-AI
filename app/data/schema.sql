-- PayPilot AI SQLite Database Schema

CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    brand TEXT NOT NULL,
    price REAL NOT NULL,
    original_price REAL,
    description TEXT,
    specs TEXT,
    features TEXT,
    reliability_score REAL NOT NULL,
    warranty_months INTEGER NOT NULL DEFAULT 12,
    delivery_days INTEGER NOT NULL DEFAULT 2,
    data_source TEXT NOT NULL,
    data_source_label TEXT NOT NULL,
    stock_quantity INTEGER NOT NULL DEFAULT 0,
    image_url TEXT,
    price_history TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_price ON products(price);
CREATE INDEX IF NOT EXISTS idx_products_reliability ON products(reliability_score);

CREATE TABLE IF NOT EXISTS bills (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    amount REAL NOT NULL,
    due_date TEXT NOT NULL,
    category TEXT NOT NULL,
    recurring INTEGER NOT NULL DEFAULT 0,
    is_paid INTEGER NOT NULL DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_bills_due_date ON bills(due_date);

CREATE TABLE IF NOT EXISTS locked_orders (
    order_id TEXT PRIMARY KEY,
    items_json TEXT NOT NULL,
    subtotal REAL NOT NULL,
    tax REAL NOT NULL,
    shipping REAL NOT NULL,
    total_amount REAL NOT NULL,
    currency TEXT NOT NULL DEFAULT 'USD',
    paypal_order_id TEXT,
    approval_url TEXT,
    status TEXT NOT NULL DEFAULT 'CREATED',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    captured_at TIMESTAMP
);
