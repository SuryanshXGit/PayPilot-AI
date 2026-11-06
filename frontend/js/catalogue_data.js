/**
 * PayPilot AI — Verified Catalogue & Benchmark Seed Dataset
 * Module: Suryansh (Frontend / Dashboard & Comparison UI)
 *
 * Hackathon Guardrails Compliance:
 * - All items carry explicit data_source and data_source_label.
 * - Price trends are disclosed as simulated Honey sample data.
 * - Used as client-side benchmark and seamless fallback when backend is offline.
 */

const VERIFIED_CATALOGUE = [
  // -------------------------------------------------------------------------
  // DESK LAMPS (Dorm Scenario)
  // -------------------------------------------------------------------------
  {
    id: "lamp-lumina-study",
    name: "Lumina Glow LED Study Lamp",
    category: "desk_lamp",
    category_label: "Desk Lamp",
    brand: "Lumina",
    price: 18.99,
    original_price: 22.99,
    description: "Compact clip-on desk lamp with 3 brightness levels. Simple plastic build for budget-conscious students.",
    specs: {
      brightness_lumens: 400,
      color_modes: 3,
      power_source: "USB-A corded",
      arm_type: "Flexible gooseneck",
      material: "ABS Plastic"
    },
    features: ["3 touch brightness modes", "Flexible 360-degree gooseneck", "Low power consumption (5W)"],
    reliability_score: 7.8,
    warranty_months: 12,
    delivery_days: 2,
    data_source: "curated_catalog_verified_retail",
    data_source_label: "Controlled Catalogue Price (Verified Retail Benchmark)",
    stock_quantity: 45,
    image_url: "https://images.unsplash.com/photo-1534353436294-0dbd4bdac845?auto=format&fit=crop&w=400&q=80",
    price_history: [
      { date: "2026-08-15", price: 24.99, source: "simulated_honey_trend" },
      { date: "2026-09-20", price: 22.99, source: "simulated_honey_trend" },
      { date: "2026-10-15", price: 18.99, source: "simulated_honey_trend" }
    ]
  },
  {
    id: "lamp-taotronics-pro",
    name: "TaoTronics Eye-Care Multi-Spectrum Desk Lamp",
    category: "desk_lamp",
    category_label: "Desk Lamp",
    brand: "TaoTronics",
    price: 32.99,
    original_price: 39.99,
    description: "High-durability anodized aluminum desk lamp with flicker-free eye protection, 5 color temperatures, and built-in USB charging port.",
    specs: {
      brightness_lumens: 650,
      color_modes: 5,
      power_source: "AC Adapter + 5V/1A USB port",
      arm_type: "Multi-angle foldable aluminum arm",
      material: "Anodized Aluminum + ABS"
    },
    features: [
      "Flicker-free eye-caring diffusion plate",
      "5 color temperatures & 6 brightness levels",
      "Built-in 5V/1A USB charging port for phone",
      "45-minute auto-off sleep timer"
    ],
    reliability_score: 9.2,
    warranty_months: 24,
    delivery_days: 1,
    data_source: "curated_catalog_verified_retail",
    data_source_label: "Controlled Catalogue Price (Verified Retail Benchmark)",
    stock_quantity: 30,
    image_url: "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=400&q=80",
    price_history: [
      { date: "2026-08-01", price: 39.99, source: "simulated_honey_trend" },
      { date: "2026-09-10", price: 36.99, source: "simulated_honey_trend" },
      { date: "2026-10-20", price: 32.99, source: "simulated_honey_trend" }
    ]
  },
  {
    id: "lamp-benq-eread",
    name: "BenQ e-Reading Architectural LED Task Light",
    category: "desk_lamp",
    category_label: "Desk Lamp",
    brand: "BenQ",
    price: 89.00,
    original_price: 99.00,
    description: "Premium wide-span curved task lamp designed for dual monitors and wide study desks with smart ambient auto-dimming.",
    specs: {
      brightness_lumens: 900,
      color_modes: 8,
      power_source: "DC Adapter",
      arm_type: "Dual-joint articulated zinc alloy arm",
      material: "Zinc alloy + Aerospace aluminum"
    },
    features: [
      "Patented curved optical head illuminates 150% wider area",
      "Built-in ambient light sensor auto-adjusts brightness",
      "Zero flicker, certified safe blue light emission",
      "Heavy-duty counterbalanced base"
    ],
    reliability_score: 9.6,
    warranty_months: 36,
    delivery_days: 2,
    data_source: "curated_catalog_verified_retail",
    data_source_label: "Controlled Catalogue Price (Verified Retail Benchmark)",
    stock_quantity: 12,
    image_url: "https://images.unsplash.com/photo-1517991104123-1d56a6e81ed9?auto=format&fit=crop&w=400&q=80",
    price_history: [
      { date: "2026-07-01", price: 109.00, source: "simulated_honey_trend" },
      { date: "2026-08-15", price: 99.00, source: "simulated_honey_trend" },
      { date: "2026-10-01", price: 89.00, source: "simulated_honey_trend" }
    ]
  },

  // -------------------------------------------------------------------------
  // PORTABLE STEAMERS (Dorm Scenario)
  // -------------------------------------------------------------------------
  {
    id: "steamer-hilife-travel",
    name: "Hilife Handheld Compact Garment Steamer",
    category: "portable_steamer",
    category_label: "Portable Steamer",
    brand: "Hilife",
    price: 24.99,
    original_price: 29.99,
    description: "Lightweight 240ml handheld travel steamer with continuous 15-minute steam output. Fits in carry-on backpacks.",
    specs: {
      water_capacity_ml: 240,
      heat_up_seconds: 120,
      steam_duration_mins: 15,
      power_watts: 700,
      weight_lbs: 1.7
    },
    features: ["Compact 240ml clear-view reservoir", "9-foot power cord for dorm convenience", "Spill-proof sealing baffle"],
    reliability_score: 8.2,
    warranty_months: 12,
    delivery_days: 2,
    data_source: "curated_catalog_verified_retail",
    data_source_label: "Controlled Catalogue Price (Verified Retail Benchmark)",
    stock_quantity: 38,
    image_url: "https://images.unsplash.com/photo-1585336261026-7f4f6e166e4a?auto=format&fit=crop&w=400&q=80",
    price_history: [
      { date: "2026-08-10", price: 29.99, source: "simulated_honey_trend" },
      { date: "2026-09-05", price: 26.99, source: "simulated_honey_trend" },
      { date: "2026-10-18", price: 24.99, source: "simulated_honey_trend" }
    ]
  },
  {
    id: "steamer-conair-turbo",
    name: "Conair Turbo Extreme Steam Handheld Fabric Steamer",
    category: "portable_steamer",
    category_label: "Portable Steamer",
    brand: "Conair",
    price: 44.99,
    original_price: 54.99,
    description: "Dual-slotted aluminum ceramic soleplate with turbo steam burst and 40-second fast heat up. Perfect for heavy dorm fabrics.",
    specs: {
      water_capacity_ml: 215,
      heat_up_seconds: 40,
      steam_duration_mins: 20,
      power_watts: 1875,
      weight_lbs: 2.3
    },
    features: [
      "Turbo charge button delivers 50% more steam",
      "Ceramic soleplate doubles as light iron",
      "3-in-1 attachment (silicone band, bristle brush, delicate fabric bonnet)",
      "QuikFast heating element"
    ],
    reliability_score: 9.4,
    warranty_months: 24,
    delivery_days: 1,
    data_source: "curated_catalog_verified_retail",
    data_source_label: "Controlled Catalogue Price (Verified Retail Benchmark)",
    stock_quantity: 26,
    image_url: "https://images.unsplash.com/photo-1585336261026-7f4f6e166e4a?auto=format&fit=crop&w=400&q=80",
    price_history: [
      { date: "2026-08-01", price: 54.99, source: "simulated_honey_trend" },
      { date: "2026-09-12", price: 49.99, source: "simulated_honey_trend" },
      { date: "2026-10-25", price: 44.99, source: "simulated_honey_trend" }
    ]
  },
  {
    id: "steamer-rowenta-xcel",
    name: "Rowenta X-Cel Steam Pro Professional Steamer",
    category: "portable_steamer",
    category_label: "Portable Steamer",
    brand: "Rowenta",
    price: 69.99,
    original_price: 79.99,
    description: "German-engineered commercial grade portable garment steamer with heated cast aluminum head and 26g/min continuous steam.",
    specs: {
      water_capacity_ml: 200,
      heat_up_seconds: 45,
      steam_duration_mins: 18,
      power_watts: 1600,
      weight_lbs: 3.1
    },
    features: ["Cast aluminum heated soleplate", "Cast-iron anti-calc system", "Heated soleplate prevents drip spots"],
    reliability_score: 9.5,
    warranty_months: 24,
    delivery_days: 2,
    data_source: "curated_catalog_verified_retail",
    data_source_label: "Controlled Catalogue Price (Verified Retail Benchmark)",
    stock_quantity: 14,
    image_url: "https://images.unsplash.com/photo-1585336261026-7f4f6e166e4a?auto=format&fit=crop&w=400&q=80",
    price_history: [
      { date: "2026-07-20", price: 84.99, source: "simulated_honey_trend" },
      { date: "2026-09-01", price: 79.99, source: "simulated_honey_trend" },
      { date: "2026-10-10", price: 69.99, source: "simulated_honey_trend" }
    ]
  },

  // -------------------------------------------------------------------------
  // NOISE-CANCELLING EARBUDS (Dorm Scenario)
  // -------------------------------------------------------------------------
  {
    id: "buds-tozo-nc9",
    name: "TOZO NC9 Hybrid Active Noise Cancelling Earbuds",
    category: "noise_cancelling_earbuds",
    category_label: "Noise Cancelling Earbuds",
    brand: "TOZO",
    price: 29.99,
    original_price: 39.99,
    description: "Budget hybrid active noise cancellation with immersive bass and IPX6 waterproof rating.",
    specs: {
      anc_depth_db: 35,
      battery_hours_buds: 10.5,
      battery_hours_total: 42,
      bluetooth_version: "5.3",
      water_resistance: "IPX6"
    },
    features: ["Hybrid 3-layer ANC reduces noise up to 35dB", "Touch controls & low latency gaming mode", "IPX6 sweatproof casing"],
    reliability_score: 8.1,
    warranty_months: 12,
    delivery_days: 2,
    data_source: "curated_catalog_verified_retail",
    data_source_label: "Controlled Catalogue Price (Verified Retail Benchmark)",
    stock_quantity: 50,
    image_url: "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&w=400&q=80",
    price_history: [
      { date: "2026-08-15", price: 39.99, source: "simulated_honey_trend" },
      { date: "2026-09-18", price: 34.99, source: "simulated_honey_trend" },
      { date: "2026-10-22", price: 29.99, source: "simulated_honey_trend" }
    ]
  },
  {
    id: "buds-anker-space-a40",
    name: "Anker Soundcore Space A40 Adaptive ANC Earbuds",
    category: "noise_cancelling_earbuds",
    category_label: "Noise Cancelling Earbuds",
    brand: "Anker",
    price: 59.99,
    original_price: 79.99,
    description: "Industry-leading auto-adaptive ANC blocking 98% of ambient noise, Hi-Res Wireless LDAC audio, and 50h total playtime.",
    specs: {
      anc_depth_db: 45,
      battery_hours_buds: 10,
      battery_hours_total: 50,
      bluetooth_version: "5.2",
      water_resistance: "IPX4"
    },
    features: [
      "Auto-detects external noise and selects ideal ANC level",
      "50-hour ultra-long battery life with wireless charging",
      "Hi-Res Wireless certified sound via LDAC codec",
      "Multi-point connection (switch laptop and phone smoothly)"
    ],
    reliability_score: 9.4,
    warranty_months: 18,
    delivery_days: 1,
    data_source: "curated_catalog_verified_retail",
    data_source_label: "Controlled Catalogue Price (Verified Retail Benchmark)",
    stock_quantity: 35,
    image_url: "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&w=400&q=80",
    price_history: [
      { date: "2026-08-01", price: 79.99, source: "simulated_honey_trend" },
      { date: "2026-09-15", price: 69.99, source: "simulated_honey_trend" },
      { date: "2026-10-20", price: 59.99, source: "simulated_honey_trend" }
    ]
  },
  {
    id: "buds-sony-wf1000xm5",
    name: "Sony WF-1000XM5 Industry Leading Flagship ANC Earbuds",
    category: "noise_cancelling_earbuds",
    category_label: "Noise Cancelling Earbuds",
    brand: "Sony",
    price: 219.99,
    original_price: 279.99,
    description: "Dual processor Integrated V2 & QN2e noise cancelling with bone conduction sensor and 24-bit audio processing.",
    specs: {
      anc_depth_db: 50,
      battery_hours_buds: 8,
      battery_hours_total: 24,
      bluetooth_version: "5.3",
      water_resistance: "IPX4"
    },
    features: [
      "Dual processors for unmatched high-frequency attenuation",
      "AI-based noise reduction algorithm with bone sensors",
      "Multipoint connection and speak-to-chat mode"
    ],
    reliability_score: 9.8,
    warranty_months: 24,
    delivery_days: 1,
    data_source: "curated_catalog_verified_retail",
    data_source_label: "Controlled Catalogue Price (Verified Retail Benchmark)",
    stock_quantity: 8,
    image_url: "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&w=400&q=80",
    price_history: [
      { date: "2026-07-01", price: 279.99, source: "simulated_honey_trend" },
      { date: "2026-08-20", price: 249.99, source: "simulated_honey_trend" },
      { date: "2026-10-01", price: 219.99, source: "simulated_honey_trend" }
    ]
  },

  // -------------------------------------------------------------------------
  // LAPTOPS (Emergency Expense Scenario)
  // -------------------------------------------------------------------------
  {
    id: "laptop-acer-aspire5",
    name: "Acer Aspire 5 Slim Business & Student Laptop",
    category: "laptop",
    category_label: "Laptop",
    brand: "Acer",
    price: 389.00,
    original_price: 449.00,
    description: "Affordable 15.6' Full HD laptop with 13th Gen Intel Core i5, 8GB RAM, and 512GB SSD. Reliable everyday daily driver.",
    specs: {
      display_size: "15.6 inch IPS FHD",
      processor: "Intel Core i5-1335U",
      ram: "8GB DDR4 (Expandable)",
      storage: "512GB NVMe SSD",
      battery_life_hours: 8.5,
      weight_lbs: 3.9
    },
    features: ["15.6 inch IPS 1080p Anti-glare screen", "Wi-Fi 6 & Thunderbolt 4 port", "Full numeric keypad"],
    reliability_score: 8.6,
    warranty_months: 12,
    delivery_days: 2,
    data_source: "curated_catalog_verified_retail",
    data_source_label: "Controlled Catalogue Price (Verified Retail Benchmark)",
    stock_quantity: 18,
    image_url: "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=400&q=80",
    price_history: [
      { date: "2026-08-01", price: 449.00, source: "simulated_honey_trend" },
      { date: "2026-09-15", price: 419.00, source: "simulated_honey_trend" },
      { date: "2026-10-20", price: 389.00, source: "simulated_honey_trend" }
    ]
  },
  {
    id: "laptop-lenovo-t14s",
    name: "Lenovo ThinkPad T14s Gen 3 (Certified Refurbished)",
    category: "laptop",
    category_label: "Laptop",
    brand: "Lenovo",
    price: 499.00,
    original_price: 1199.00,
    description: "MIL-SPEC tested enterprise business ultra-book with AMD Ryzen 7 PRO, 16GB RAM, 512GB SSD, spill-resistant keyboard, and fast 1-day delivery.",
    specs: {
      display_size: "14 inch 1920x1200 Low Power IPS",
      processor: "AMD Ryzen 7 PRO 6850U (8-Core)",
      ram: "16GB LPDDR5",
      storage: "512GB PCIe 4.0 SSD",
      battery_life_hours: 14.0,
      weight_lbs: 2.7
    },
    features: [
      "Legendary spill-resistant ThinkPad keyboard with TrackPoint",
      "Magnesium-aluminum hybrid chassis tested against 12 military standards",
      "Certified Grade-A Refurbished with full 1-year hardware replacement warranty",
      "RapidCharge: 80% charge in 60 minutes",
      "Next-Day Express Dispatch Guarantee"
    ],
    reliability_score: 9.6,
    warranty_months: 12,
    delivery_days: 1,
    data_source: "curated_catalog_verified_retail",
    data_source_label: "Controlled Catalogue Price (Verified Retail Benchmark)",
    stock_quantity: 7,
    image_url: "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?auto=format&fit=crop&w=400&q=80",
    price_history: [
      { date: "2026-08-01", price: 549.00, source: "simulated_honey_trend" },
      { date: "2026-09-10", price: 529.00, source: "simulated_honey_trend" },
      { date: "2026-10-25", price: 499.00, source: "simulated_honey_trend" }
    ]
  },
  {
    id: "laptop-dell-xps13",
    name: "Dell XPS 13 Plus Premium Ultrabook",
    category: "laptop",
    category_label: "Laptop",
    brand: "Dell",
    price: 899.00,
    original_price: 1299.00,
    description: "Flagship premium laptop with borderless InfinityEdge 3.5K OLED display and CNC machined aluminum.",
    specs: {
      display_size: "13.4 inch 3.5K OLED InfinityEdge",
      processor: "Intel Core i7-1360P",
      ram: "16GB LPDDR5",
      storage: "1TB PCIe NVMe SSD",
      battery_life_hours: 10.0,
      weight_lbs: 2.7
    },
    features: ["Zero-lattice keyboard with capacitive touch row", "Seamless glass touchpad", "CNC machined aluminum casing"],
    reliability_score: 9.7,
    warranty_months: 24,
    delivery_days: 2,
    data_source: "curated_catalog_verified_retail",
    data_source_label: "Controlled Catalogue Price (Verified Retail Benchmark)",
    stock_quantity: 5,
    image_url: "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?auto=format&fit=crop&w=400&q=80",
    price_history: [
      { date: "2026-08-01", price: 1199.00, source: "simulated_honey_trend" },
      { date: "2026-09-10", price: 999.00, source: "simulated_honey_trend" },
      { date: "2026-10-25", price: 899.00, source: "simulated_honey_trend" }
    ]
  }
];

// -------------------------------------------------------------------------
// INITIAL USER BILLS (7-Day Financial Health Monitoring)
// -------------------------------------------------------------------------
const INITIAL_BILLS = [
  {
    id: "bill-elec-001",
    title: "Dorm Electric & Utility Bill",
    category: "Utilities",
    amount: 45.00,
    due_date: "2026-11-07", // 3 days from reference date 2026-11-04
    is_recurring: true,
    frequency: "monthly"
  },
  {
    id: "bill-wifi-002",
    title: "Campus High-Speed WiFi Subscription",
    category: "Internet",
    amount: 35.00,
    due_date: "2026-11-09", // 5 days from reference date 2026-11-04
    is_recurring: true,
    frequency: "monthly"
  },
  {
    id: "bill-spotify-003",
    title: "Spotify Student Premium",
    category: "Entertainment",
    amount: 10.99,
    due_date: "2026-11-22", // 18 days away (outside 7-day window)
    is_recurring: true,
    frequency: "monthly"
  },
  {
    id: "bill-rent-004",
    title: "Monthly Student Housing Installment",
    category: "Housing",
    amount: 650.00,
    due_date: "2026-11-29", // 25 days away (outside 7-day window)
    is_recurring: true,
    frequency: "monthly"
  }
];

// Export to window
if (typeof window !== "undefined") {
  window.VERIFIED_CATALOGUE = VERIFIED_CATALOGUE;
  window.INITIAL_BILLS = INITIAL_BILLS;
}
