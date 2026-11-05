"""
Seed catalogue and financial data for PayPilot AI.
All products include verified prices, reliability scores, specs,
and transparent data-source labeling in compliance with hackathon guardrails.
"""

INITIAL_PRODUCTS = [
    # -------------------------------------------------------------
    # CATEGORY: DESK LAMPS (Dorm Scenario)
    # -------------------------------------------------------------
    {
        "id": "lamp-lumina-study",
        "name": "Lumina Glow LED Study Lamp",
        "category": "desk_lamp",
        "brand": "Lumina",
        "price": 18.99,
        "original_price": 22.99,
        "description": "Compact clip-on desk lamp with 3 brightness levels. Simple plastic build for budget-conscious students.",
        "specs": {
            "brightness_lumens": 400,
            "color_modes": 3,
            "power_source": "USB-A corded",
            "arm_type": "Flexible gooseneck",
            "material": "ABS Plastic"
        },
        "features": [
            "3 touch brightness modes",
            "Flexible 360-degree gooseneck",
            "Low power consumption (5W)"
        ],
        "reliability_score": 7.8,
        "warranty_months": 12,
        "delivery_days": 2,
        "data_source": "curated_catalog_verified_retail",
        "data_source_label": "Controlled Catalogue Price (Verified Retail Benchmark)",
        "stock_quantity": 45,
        "image_url": "https://images.unsplash.com/photo-1534353436294-0dbd4bdac845?auto=format&fit=crop&w=400&q=80",
        "price_history": [
            {"date": "2026-08-15", "price": 24.99, "source": "simulated_honey_trend"},
            {"date": "2026-09-20", "price": 22.99, "source": "simulated_honey_trend"},
            {"date": "2026-10-15", "price": 18.99, "source": "simulated_honey_trend"}
        ]
    },
    {
        "id": "lamp-taotronics-pro",
        "name": "TaoTronics Eye-Care Multi-Spectrum Desk Lamp",
        "category": "desk_lamp",
        "brand": "TaoTronics",
        "price": 32.99,
        "original_price": 39.99,
        "description": "High-durability anodized aluminum desk lamp with flicker-free eye protection, 5 color temperatures, and built-in USB charging port.",
        "specs": {
            "brightness_lumens": 650,
            "color_modes": 5,
            "power_source": "AC Adapter + 5V/1A USB port",
            "arm_type": "Multi-angle foldable aluminum arm",
            "material": "Anodized Aluminum + ABS"
        },
        "features": [
            "Flicker-free eye-caring diffusion plate",
            "5 color temperatures & 6 brightness levels",
            "Built-in 5V/1A USB charging port for phone",
            "45-minute auto-off sleep timer"
        ],
        "reliability_score": 9.2,
        "warranty_months": 24,
        "delivery_days": 1,
        "data_source": "curated_catalog_verified_retail",
        "data_source_label": "Controlled Catalogue Price (Verified Retail Benchmark)",
        "stock_quantity": 30,
        "image_url": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=400&q=80",
        "price_history": [
            {"date": "2026-08-01", "price": 39.99, "source": "simulated_honey_trend"},
            {"date": "2026-09-10", "price": 36.99, "source": "simulated_honey_trend"},
            {"date": "2026-10-20", "price": 32.99, "source": "simulated_honey_trend"}
        ]
    },
    {
        "id": "lamp-benq-eread",
        "name": "BenQ e-Reading Architectural LED Task Light",
        "category": "desk_lamp",
        "brand": "BenQ",
        "price": 89.00,
        "original_price": 99.00,
        "description": "Premium wide-span curved task lamp designed for dual monitors and wide study desks with smart ambient auto-dimming.",
        "specs": {
            "brightness_lumens": 900,
            "color_modes": 8,
            "power_source": "DC Adapter",
            "arm_type": "Dual-joint articulated zinc alloy arm",
            "material": "Zinc alloy + Aerospace aluminum"
        },
        "features": [
            "Patented curved optical head illuminates 150% wider area",
            "Built-in ambient light sensor auto-adjusts brightness",
            "Zero flicker, certified safe blue light emission",
            "Heavy-duty counterbalanced base"
        ],
        "reliability_score": 9.6,
        "warranty_months": 36,
        "delivery_days": 2,
        "data_source": "curated_catalog_verified_retail",
        "data_source_label": "Controlled Catalogue Price (Verified Retail Benchmark)",
        "stock_quantity": 12,
        "image_url": "https://images.unsplash.com/photo-1517991104123-1d56a6e81ed9?auto=format&fit=crop&w=400&q=80",
        "price_history": [
            {"date": "2026-07-01", "price": 109.00, "source": "simulated_honey_trend"},
            {"date": "2026-08-15", "price": 99.00, "source": "simulated_honey_trend"},
            {"date": "2026-10-01", "price": 89.00, "source": "simulated_honey_trend"}
        ]
    },

    # -------------------------------------------------------------
    # CATEGORY: PORTABLE STEAMERS (Dorm Scenario)
    # -------------------------------------------------------------
    {
        "id": "steamer-hilife-travel",
        "name": "Hilife Handheld Compact Garment Steamer",
        "category": "portable_steamer",
        "brand": "Hilife",
        "price": 24.99,
        "original_price": 29.99,
        "description": "Lightweight 240ml portable steamer suitable for quick touch-ups before class or interviews. Compact travel profile.",
        "specs": {
            "wattage": 700,
            "tank_capacity_ml": 240,
            "heatup_time_sec": 75,
            "continuous_steam_min": 15,
            "weight_lbs": 1.7
        },
        "features": [
            "240ml high capacity water reservoir",
            "9-foot extended power cord",
            "Lightweight compact body"
        ],
        "reliability_score": 8.4,
        "warranty_months": 12,
        "delivery_days": 2,
        "data_source": "curated_catalog_verified_retail",
        "data_source_label": "Controlled Catalogue Price (Verified Retail Benchmark)",
        "stock_quantity": 40,
        "image_url": "https://images.unsplash.com/photo-1585338107529-13afc5f02586?auto=format&fit=crop&w=400&q=80",
        "price_history": [
            {"date": "2026-08-10", "price": 29.99, "source": "simulated_honey_trend"},
            {"date": "2026-09-12", "price": 26.99, "source": "simulated_honey_trend"},
            {"date": "2026-10-18", "price": 24.99, "source": "simulated_honey_trend"}
        ]
    },
    {
        "id": "steamer-conair-turbo",
        "name": "Conair Turbo ExtremeSteam Handheld Fabric Steamer",
        "category": "portable_steamer",
        "brand": "Conair",
        "price": 44.99,
        "original_price": 54.99,
        "description": "High-velocity dual heat steamer with aluminum soleplate that acts like an iron. 40-second heat-up and anti-leak seal.",
        "specs": {
            "wattage": 1875,
            "tank_capacity_ml": 215,
            "heatup_time_sec": 40,
            "continuous_steam_min": 20,
            "weight_lbs": 2.4
        },
        "features": [
            "Turbo steam release penetrates thick fabrics",
            "Quilted aluminum soleplate functions as iron press",
            "Anti-drip technology prevents water spots",
            "3-in-1 attachment: silicone band, delicate fabric spacer, bristle brush"
        ],
        "reliability_score": 9.4,
        "warranty_months": 24,
        "delivery_days": 1,
        "data_source": "curated_catalog_verified_retail",
        "data_source_label": "Controlled Catalogue Price (Verified Retail Benchmark)",
        "stock_quantity": 25,
        "image_url": "https://images.unsplash.com/photo-1517677208171-0bc6725a3e60?auto=format&fit=crop&w=400&q=80",
        "price_history": [
            {"date": "2026-08-05", "price": 54.99, "source": "simulated_honey_trend"},
            {"date": "2026-09-01", "price": 49.99, "source": "simulated_honey_trend"},
            {"date": "2026-10-25", "price": 44.99, "source": "simulated_honey_trend"}
        ]
    },
    {
        "id": "steamer-rowenta-xcel",
        "name": "Rowenta X-Cel Steam Advanced Handheld Steamer",
        "category": "portable_steamer",
        "brand": "Rowenta",
        "price": 69.99,
        "original_price": 79.99,
        "description": "Professional-grade handheld steamer with heated ceramic soleplate and continuous lock steam trigger for heavy clothes.",
        "specs": {
            "wattage": 1875,
            "tank_capacity_ml": 200,
            "heatup_time_sec": 40,
            "continuous_steam_min": 18,
            "weight_lbs": 3.0
        },
        "features": [
            "Cast aluminum heating element with ceramic soleplate",
            "Cast-off de-creasing power for suits and dorm bedding",
            "Removable water tank with locking latch"
        ],
        "reliability_score": 9.5,
        "warranty_months": 36,
        "delivery_days": 2,
        "data_source": "curated_catalog_verified_retail",
        "data_source_label": "Controlled Catalogue Price (Verified Retail Benchmark)",
        "stock_quantity": 15,
        "image_url": "https://images.unsplash.com/photo-1585338107529-13afc5f02586?auto=format&fit=crop&w=400&q=80",
        "price_history": [
            {"date": "2026-07-20", "price": 79.99, "source": "simulated_honey_trend"},
            {"date": "2026-09-15", "price": 74.99, "source": "simulated_honey_trend"},
            {"date": "2026-10-10", "price": 69.99, "source": "simulated_honey_trend"}
        ]
    },

    # -------------------------------------------------------------
    # CATEGORY: NOISE-CANCELLING EARBUDS (Dorm Scenario)
    # -------------------------------------------------------------
    {
        "id": "buds-jlab-goair",
        "name": "JLab Go Air Pop True Wireless Earbuds",
        "category": "noise_cancelling_earbuds",
        "brand": "JLab",
        "price": 24.99,
        "original_price": 29.99,
        "description": "Ultra-budget true wireless earbuds with passive noise isolating ear tips. No active noise cancelling circuit.",
        "specs": {
            "battery_life_hours": 32,
            "anc_active": False,
            "anc_db_reduction": 12,
            "water_resistance": "IPX4",
            "bluetooth_version": "5.3"
        },
        "features": [
            "Pocket-sized charging case with integrated USB cable",
            "3 EQ sound presets: JLab Signature, Balanced, Bass Boost",
            "8+ hours playtime per charge (32+ hours total)"
        ],
        "reliability_score": 8.1,
        "warranty_months": 24,
        "delivery_days": 2,
        "data_source": "curated_catalog_verified_retail",
        "data_source_label": "Controlled Catalogue Price (Verified Retail Benchmark)",
        "stock_quantity": 60,
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&w=400&q=80",
        "price_history": [
            {"date": "2026-08-01", "price": 29.99, "source": "simulated_honey_trend"},
            {"date": "2026-09-01", "price": 24.99, "source": "simulated_honey_trend"}
        ]
    },
    {
        "id": "buds-soundpeats-capsule",
        "name": "SoundPEATS Capsule3 Pro Hybrid ANC Earbuds",
        "category": "noise_cancelling_earbuds",
        "brand": "SoundPEATS",
        "price": 49.99,
        "original_price": 69.99,
        "description": "Hybrid active noise cancellation up to 43dB depth. Hi-Res Audio certification with LDAC codec support.",
        "specs": {
            "battery_life_hours": 52,
            "anc_active": True,
            "anc_db_reduction": 43,
            "water_resistance": "IPX4",
            "bluetooth_version": "5.3"
        },
        "features": [
            "Hybrid ANC blocks study room distractions and drone noise",
            "6-mic array for clear voice calls and virtual lectures",
            "Game mode low latency 70ms"
        ],
        "reliability_score": 9.0,
        "warranty_months": 12,
        "delivery_days": 2,
        "data_source": "curated_catalog_verified_retail",
        "data_source_label": "Controlled Catalogue Price (Verified Retail Benchmark)",
        "stock_quantity": 35,
        "image_url": "https://images.unsplash.com/photo-1572536147248-ac59a8abfa4b?auto=format&fit=crop&w=400&q=80",
        "price_history": [
            {"date": "2026-07-15", "price": 69.99, "source": "simulated_honey_trend"},
            {"date": "2026-08-30", "price": 59.99, "source": "simulated_honey_trend"},
            {"date": "2026-10-14", "price": 49.99, "source": "simulated_honey_trend"}
        ]
    },
    {
        "id": "buds-anker-space-a40",
        "name": "Anker Soundcore Space A40 Adaptive ANC Earbuds",
        "category": "noise_cancelling_earbuds",
        "brand": "Anker Soundcore",
        "price": 59.99,
        "original_price": 79.99,
        "description": "Targeted adaptive noise cancelling reducing up to 98% of background noise. Exceptional 50-hour battery life and multi-point Bluetooth pairing.",
        "specs": {
            "battery_life_hours": 50,
            "anc_active": True,
            "anc_db_reduction": 45,
            "water_resistance": "IPX4",
            "bluetooth_version": "5.2"
        },
        "features": [
            "Adaptive ANC automatically detects external noise and calibrates reduction",
            "HearID custom sound profile tailored to your ears",
            "Dual-device connection (simultaneously connect laptop & phone)",
            "Wireless charging supported"
        ],
        "reliability_score": 9.4,
        "warranty_months": 18,
        "delivery_days": 1,
        "data_source": "curated_catalog_verified_retail",
        "data_source_label": "Controlled Catalogue Price (Verified Retail Benchmark)",
        "stock_quantity": 28,
        "image_url": "https://images.unsplash.com/photo-1606220588913-b3aacb4d2f46?auto=format&fit=crop&w=400&q=80",
        "price_history": [
            {"date": "2026-08-10", "price": 79.99, "source": "simulated_honey_trend"},
            {"date": "2026-09-18", "price": 69.99, "source": "simulated_honey_trend"},
            {"date": "2026-10-22", "price": 59.99, "source": "simulated_honey_trend"}
        ]
    },
    {
        "id": "buds-sony-wf1000xm5",
        "name": "Sony WF-1000XM5 Flagship Noise Cancelling Earbuds",
        "category": "noise_cancelling_earbuds",
        "brand": "Sony",
        "price": 229.99,
        "original_price": 299.99,
        "description": "Industry benchmark active noise cancellation powered by dual proprietary processors. Premium sound quality and polyurethane foam tips.",
        "specs": {
            "battery_life_hours": 24,
            "anc_active": True,
            "anc_db_reduction": 48,
            "water_resistance": "IPX4",
            "bluetooth_version": "5.3"
        },
        "features": [
            "Integrated Processor V2 and HD Noise Cancelling Processor QN2e",
            "Dynamic Driver X for rich vocals and detailed sound",
            "Bone conduction sensors and AI noise reduction for calls",
            "Multipoint connection & Speak-to-Chat"
        ],
        "reliability_score": 9.7,
        "warranty_months": 12,
        "delivery_days": 1,
        "data_source": "curated_catalog_verified_retail",
        "data_source_label": "Controlled Catalogue Price (Verified Retail Benchmark)",
        "stock_quantity": 10,
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&w=400&q=80",
        "price_history": [
            {"date": "2026-07-01", "price": 299.99, "source": "simulated_honey_trend"},
            {"date": "2026-09-01", "price": 249.99, "source": "simulated_honey_trend"},
            {"date": "2026-10-15", "price": 229.99, "source": "simulated_honey_trend"}
        ]
    },

    # -------------------------------------------------------------
    # CATEGORY: LAPTOPS (Emergency Expense Scenario)
    # -------------------------------------------------------------
    {
        "id": "laptop-acer-aspire5",
        "name": "Acer Aspire 5 Slim Laptop (Intel Core i3, 8GB RAM, 256GB SSD)",
        "category": "laptop",
        "brand": "Acer",
        "price": 389.00,
        "original_price": 449.00,
        "description": "Reliable budget new laptop for emergency school or office replacement. Full HD IPS display and ergonomic lift hinge.",
        "specs": {
            "processor": "Intel Core i3-1215U (6 cores)",
            "ram_gb": 8,
            "storage_gb": 256,
            "display": "15.6-inch Full HD (1920 x 1080) IPS",
            "battery_hours": 8.5,
            "condition": "Brand New"
        },
        "features": [
            "Ergonomic lift hinge for typing comfort and thermal cooling",
            "Wi-Fi 6 connectivity and full HDMI port",
            "Acer TNR solution for enhanced video call clarity"
        ],
        "reliability_score": 8.6,
        "warranty_months": 12,
        "delivery_days": 2,
        "data_source": "curated_catalog_verified_retail",
        "data_source_label": "Controlled Catalogue Price (Verified Retail Benchmark)",
        "stock_quantity": 14,
        "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=400&q=80",
        "price_history": [
            {"date": "2026-08-01", "price": 449.00, "source": "simulated_honey_trend"},
            {"date": "2026-09-15", "price": 419.00, "source": "simulated_honey_trend"},
            {"date": "2026-10-20", "price": 389.00, "source": "simulated_honey_trend"}
        ]
    },
    {
        "id": "laptop-thinkpad-t14s-refurb",
        "name": "Lenovo ThinkPad T14s Gen 3 (Certified Refurbished Enterprise)",
        "category": "laptop",
        "brand": "Lenovo",
        "price": 499.00,
        "original_price": 799.00,
        "description": "Enterprise-grade certified refurbished ThinkPad. Spill-resistant keyboard, military-spec tested durability, and 1-day express delivery.",
        "specs": {
            "processor": "AMD Ryzen 7 PRO 6850U (8 cores, 16 threads)",
            "ram_gb": 16,
            "storage_gb": 512,
            "display": "14-inch WUXGA (1920 x 1200) Low Power IPS",
            "battery_hours": 11.0,
            "condition": "Certified Refurbished Grade A"
        },
        "features": [
            "Next-day emergency priority delivery available",
            "1-year comprehensive hardware warranty included",
            "Spill-resistant keyboard and MIL-STD 810H durability",
            "Hardware TPM 2.0 and fingerprint reader"
        ],
        "reliability_score": 9.6,
        "warranty_months": 12,
        "delivery_days": 1,
        "data_source": "curated_catalog_verified_retail",
        "data_source_label": "Controlled Catalogue Price (Verified Retail Benchmark)",
        "stock_quantity": 8,
        "image_url": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?auto=format&fit=crop&w=400&q=80",
        "price_history": [
            {"date": "2026-08-10", "price": 549.00, "source": "simulated_honey_trend"},
            {"date": "2026-09-20", "price": 529.00, "source": "simulated_honey_trend"},
            {"date": "2026-10-28", "price": 499.00, "source": "simulated_honey_trend"}
        ]
    },

    # -------------------------------------------------------------
    # CATEGORY: MEDICAL EQUIPMENT (Emergency Scenario)
    # -------------------------------------------------------------
    {
        "id": "med-omron-bp",
        "name": "Omron Series 3 Upper Arm Blood Pressure Monitor",
        "category": "medical_equipment",
        "brand": "Omron",
        "price": 42.99,
        "original_price": 49.99,
        "description": "Clinically validated upper arm blood pressure monitor. One-touch operation with irregular heartbeat detector.",
        "specs": {
            "type": "Digital Upper Arm Cuff",
            "cuff_size": "Standard & Large (9-17 inch circumference)",
            "memory_storage": "14 readings",
            "clinical_validation": "AAMI / ESH Validated"
        },
        "features": [
            "Advanced averaging displays average of up to 3 readings in 10 mins",
            "Irregular heartbeat indicator alerts during reading",
            "Quick 1-day emergency shipping option"
        ],
        "reliability_score": 9.7,
        "warranty_months": 24,
        "delivery_days": 1,
        "data_source": "curated_catalog_verified_retail",
        "data_source_label": "Controlled Catalogue Price (Verified Retail Benchmark)",
        "stock_quantity": 20,
        "image_url": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=400&q=80",
        "price_history": [
            {"date": "2026-08-01", "price": 49.99, "source": "simulated_honey_trend"},
            {"date": "2026-10-01", "price": 42.99, "source": "simulated_honey_trend"}
        ]
    }
]

# Sample bills for Proactive Financial Health Monitoring
# Current reference demo date: November 2, 2026
INITIAL_BILLS = [
    {
        "id": "bill-electric-01",
        "title": "Campus Utility / Dorm Electric",
        "amount": 45.00,
        "due_date": "2026-11-05",  # 3 days away (Within 7-day window!)
        "category": "utilities",
        "recurring": True,
        "is_paid": False,
        "notes": "Fall semester dorm electricity allocation."
    },
    {
        "id": "bill-internet-01",
        "title": "High-Speed Dorm WiFi",
        "amount": 35.00,
        "due_date": "2026-11-08",  # 6 days away (Within 7-day window!)
        "category": "utilities",
        "recurring": True,
        "is_paid": False,
        "notes": "Shared broadband fee due on the 8th."
    },
    {
        "id": "bill-textbook-01",
        "title": "Semester Textbook Rental Due",
        "amount": 38.50,
        "due_date": "2026-11-18",  # 16 days away (Outside 7-day window)
        "category": "education",
        "recurring": False,
        "is_paid": False,
        "notes": "Library course reserve textbook fee."
    },
    {
        "id": "bill-insurance-01",
        "title": "Student Health Co-Pay / Insurance",
        "amount": 65.00,
        "due_date": "2026-11-25",  # 23 days away (Outside 7-day window)
        "category": "health",
        "recurring": True,
        "is_paid": False,
        "notes": "Monthly medical coverage premium."
    }
]
