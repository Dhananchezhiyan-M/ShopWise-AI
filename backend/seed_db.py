import datetime
import random
import json
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.core.init_db import init_db
from app.models import (
    Store,
    CanonicalProduct,
    ProductVariant,
    StoreListing,
    PriceHistoryRecord,
)

# Set seed for reproducible prices
random.seed(42)


import sys
import io

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def generate_90_day_history(current_price: float, base_mrp: float, trend_type: str = "normal"):

    """
    Generates realistic daily price history records over the last 90 days.
    trend_type options: 'drop' (recently dropped), 'spike' (recent hike), 'normal' (minor fluctuations)
    """
    history = []
    now = datetime.datetime.utcnow()

    # Determine 90-day base baseline
    if trend_type == "drop":
        # Price was higher 90 days ago and recently dropped (Good buy)
        baseline = current_price * random.uniform(1.08, 1.15)
    elif trend_type == "spike":
        # Price was lower and recently spiked (Wait recommendation)
        baseline = current_price * random.uniform(0.88, 0.94)
    else:
        baseline = current_price * random.uniform(0.98, 1.05)

    for days_ago in range(90, 0, -1):
        record_date = now - datetime.timedelta(days=days_ago)
        
        # Festival sale dip around day 40-45
        if 40 <= days_ago <= 45:
            day_price = baseline * random.uniform(0.85, 0.90)  # Flash sale low
        elif days_ago <= 10:
            # Gradual convergence to current price
            weight = (10 - days_ago) / 10.0
            day_price = (1 - weight) * baseline + weight * current_price
        else:
            day_price = baseline * random.uniform(0.96, 1.04)

        # Round to nearest 10 or 99
        day_price = round(day_price / 10) * 10 - 1 if day_price > 1000 else round(day_price)
        history.append((record_date, float(day_price)))

    # Today's price
    history.append((now, float(current_price)))
    return history


def seed_database():
    print("[INFO] Initializing Database Schema...")
    init_db()
    db: Session = SessionLocal()

    try:
        # Check if already seeded
        if db.query(CanonicalProduct).count() > 0:
            print("[INFO] Database already contains product data. Clearing old seed data for fresh re-seed...")
            db.query(PriceHistoryRecord).delete()
            db.query(StoreListing).delete()
            db.query(ProductVariant).delete()
            db.query(CanonicalProduct).delete()
            db.query(Store).delete()
            db.commit()

        print("[INFO] 1. Seeding Stores (Amazon, Flipkart, Croma)...")
        stores_data = [
            {
                "name": "Amazon India",
                "slug": "amazon",
                "logo_url": "https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg",
                "base_url": "https://www.amazon.in",
            },
            {
                "name": "Flipkart",
                "slug": "flipkart",
                "logo_url": "https://upload.wikimedia.org/wikipedia/commons/7/7a/Flipkart_logo.svg",
                "base_url": "https://www.flipkart.com",
            },
            {
                "name": "Croma",
                "slug": "croma",
                "logo_url": "https://upload.wikimedia.org/wikipedia/commons/e/e0/Croma_Logo.png",
                "base_url": "https://www.croma.com",
            },
        ]

        store_objects = {}
        for s_data in stores_data:
            store = Store(**s_data)
            db.add(store)
            db.flush()
            store_objects[store.slug] = store

        print("[INFO] 2. Seeding Multi-Store Catalog with 90-Day Price History...")

        # Rich Product Catalog across Laptops, Audio, and Smartphones
        catalog = [
            # --------------------------- LAPTOPS ---------------------------
            {
                "title": "Lenovo IdeaPad Slim 3 15IAH8 (Intel Core i5 12th Gen)",
                "brand": "Lenovo",
                "category": "laptop",
                "base_model": "IdeaPad Slim 3",
                "image_url": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=600&auto=format&fit=crop&q=80",
                "description": "Thin and light laptop equipped with 12th Gen Intel Core i5-12450H, 16GB RAM, and 512GB SSD for coding and multitasking.",
                "variants": [
                    {
                        "variant_name": "16GB RAM / 512GB SSD / Intel Core i5 12th Gen / Arctic Grey",
                        "sku": "LEN-SLIM3-16-512-GRY",
                        "ram_gb": 16,
                        "storage_gb": 512,
                        "cpu_processor": "Intel Core i5-12450H (8 Cores, Up to 4.4GHz)",
                        "gpu_graphics": "Intel UHD Graphics",
                        "screen_size_inch": 15.6,
                        "battery_specs": "47Wh (Up to 7 Hours Battery Life, Rapid Charge)",
                        "color": "Arctic Grey",
                        "trend_type": "drop",  # Price is currently below 90-day avg (BUY NOW)
                        "listings": [
                            {
                                "store_slug": "amazon",
                                "external_product_id": "B0CX24LEN1",
                                "product_url": "https://www.amazon.in/dp/B0CX24LEN1",
                                "title_in_store": "Lenovo IdeaPad Slim 3 12th Gen Intel Core i5-12450H 15.6\" FHD Laptop (16GB/512GB SSD/Win 11/MSO 21/Grey/1.62Kg)",
                                "current_price": 55999.0,
                                "original_mrp": 72990.0,
                                "discount_percent": 23.0,
                                "rating_star": 4.4,
                                "rating_count": 8210,
                            },
                            {
                                "store_slug": "flipkart",
                                "external_product_id": "LPTLEN15IAH8",
                                "product_url": "https://www.flipkart.com/lenovo-ideapad-slim-3-intel-core-i5-12th-gen/p/itmlen15iah8",
                                "title_in_store": "Lenovo Slim 3 Intel Core i5 12th Gen 12450H - (16 GB/512 GB SSD/Windows 11 Home) 15IAH8 Thin and Light Laptop",
                                "current_price": 56490.0,
                                "original_mrp": 72990.0,
                                "discount_percent": 22.5,
                                "rating_star": 4.3,
                                "rating_count": 7980,
                            },
                            {
                                "store_slug": "croma",
                                "external_product_id": "CRM-278910",
                                "product_url": "https://www.croma.com/lenovo-ideapad-slim-3-intel-i5-16gb-512gb/p/278910",
                                "title_in_store": "Lenovo IdeaPad Slim 3 Intel Core i5 12th Gen (15.6 Inch, 16GB, 512GB SSD, Windows 11, MS Office, Arctic Grey)",
                                "current_price": 57999.0,
                                "original_mrp": 72990.0,
                                "discount_percent": 20.5,
                                "rating_star": 4.5,
                                "rating_count": 1240,
                            },
                        ],
                    }
                ],
            },
            {
                "title": "HP Pavilion 15 (AMD Ryzen 5 5625U)",
                "brand": "HP",
                "category": "laptop",
                "base_model": "Pavilion 15",
                "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop&q=80",
                "description": "Premium aluminum build laptop with AMD Ryzen 5, 16GB DDR4 RAM, and FHD IPS Micro-edge display with audio by B&O.",
                "variants": [
                    {
                        "variant_name": "16GB RAM / 512GB SSD / AMD Ryzen 5 5625U / Natural Silver",
                        "sku": "HP-PAV15-16-512-SLV",
                        "ram_gb": 16,
                        "storage_gb": 512,
                        "cpu_processor": "AMD Ryzen 5 5625U (6 Cores, 12 Threads)",
                        "gpu_graphics": "AMD Radeon Graphics",
                        "screen_size_inch": 15.6,
                        "battery_specs": "41Wh (Up to 8.5 Hours, Fast Charge)",
                        "color": "Natural Silver",
                        "trend_type": "normal",
                        "listings": [
                            {
                                "store_slug": "amazon",
                                "external_product_id": "B0B56HP15A",
                                "product_url": "https://www.amazon.in/dp/B0B56HP15A",
                                "title_in_store": "HP Pavilion 15 AMD Ryzen 5 5625U 15.6 inch(39.6cm) FHD IPS Laptop (16GB RAM/512GB SSD/B&O Audio/Silver)",
                                "current_price": 57499.0,
                                "original_mrp": 69990.0,
                                "discount_percent": 18.0,
                                "rating_star": 4.2,
                                "rating_count": 6100,
                            },
                            {
                                "store_slug": "flipkart",
                                "external_product_id": "LPTHP5625U",
                                "product_url": "https://www.flipkart.com/hp-pavilion-ryzen-5-hexa-core-5625u/p/itmhp5625u",
                                "title_in_store": "HP Pavilion AMD Ryzen 5 Hexa Core 5625U - (16 GB/512 GB SSD/Windows 11 Home) 15-eh2047AU Laptop",
                                "current_price": 56999.0,
                                "original_mrp": 69990.0,
                                "discount_percent": 18.5,
                                "rating_star": 4.3,
                                "rating_count": 5400,
                            },
                            {
                                "store_slug": "croma",
                                "external_product_id": "CRM-265431",
                                "product_url": "https://www.croma.com/hp-pavilion-15-ryzen-5-16gb-512gb/p/265431",
                                "title_in_store": "HP Pavilion 15-eh2047AU Ryzen 5 (15.6 Inch, 16GB, 512GB, Windows 11 Home, MS Office, Silver)",
                                "current_price": 58490.0,
                                "original_mrp": 69990.0,
                                "discount_percent": 16.4,
                                "rating_star": 4.4,
                                "rating_count": 980,
                            },
                        ],
                    }
                ],
            },
            {
                "title": "Acer Aspire 7 Gaming Laptop (Intel i5 12th Gen / RTX 2050)",
                "brand": "Acer",
                "category": "laptop",
                "base_model": "Aspire 7",
                "image_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=600&auto=format&fit=crop&q=80",
                "description": "High performance gaming & programming laptop with dedicated NVIDIA GeForce RTX 2050 (4GB VRAM) and 144Hz display.",
                "variants": [
                    {
                        "variant_name": "16GB RAM / 512GB SSD / Intel Core i5 12th Gen / RTX 2050 / Charcoal Black",
                        "sku": "ACER-ASP7-16-512-BLK",
                        "ram_gb": 16,
                        "storage_gb": 512,
                        "cpu_processor": "Intel Core i5-12450H (8 Cores)",
                        "gpu_graphics": "NVIDIA GeForce RTX 2050 (4GB GDDR6)",
                        "screen_size_inch": 15.6,
                        "battery_specs": "50Wh (Up to 5.5 Hours)",
                        "color": "Charcoal Black",
                        "trend_type": "drop",
                        "listings": [
                            {
                                "store_slug": "amazon",
                                "external_product_id": "B0C5R7ACER",
                                "product_url": "https://www.amazon.in/dp/B0C5R7ACER",
                                "title_in_store": "Acer Aspire 7 Intel Core i5 12th Gen 15.6\" FHD 144Hz Gaming Laptop (16GB RAM/512GB SSD/RTX 2050/Win 11)",
                                "current_price": 54990.0,
                                "original_mrp": 78990.0,
                                "discount_percent": 30.0,
                                "rating_star": 4.1,
                                "rating_count": 4500,
                            },
                            {
                                "store_slug": "flipkart",
                                "external_product_id": "LPTACERASP7",
                                "product_url": "https://www.flipkart.com/acer-aspire-7-core-i5-12th-gen-16-gb-512-gb-ssd/p/itmasp7rtx",
                                "title_in_store": "Acer Aspire 7 Intel Core i5 12th Gen 12450H - (16 GB/512 GB SSD/4 GB Graphics/NVIDIA RTX 2050/144 Hz)",
                                "current_price": 53990.0,
                                "original_mrp": 78990.0,
                                "discount_percent": 31.5,
                                "rating_star": 4.2,
                                "rating_count": 8200,
                            },
                        ],
                    }
                ],
            },
            {
                "title": "Apple MacBook Air M2 Chip (13.6-inch Liquid Retina)",
                "brand": "Apple",
                "category": "laptop",
                "base_model": "MacBook Air M2",
                "image_url": "https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=600&auto=format&fit=crop&q=80",
                "description": "Incredibly thin laptop with Apple M2 8-core CPU, 13.6-inch Liquid Retina display, 18 hours battery life, and silent fanless design.",
                "variants": [
                    {
                        "variant_name": "8GB Unified Memory / 256GB SSD / Apple M2 / Midnight",
                        "sku": "APL-MBA-M2-8-256-MID",
                        "ram_gb": 8,
                        "storage_gb": 256,
                        "cpu_processor": "Apple M2 (8-Core CPU, 8-Core GPU)",
                        "gpu_graphics": "Apple 8-Core Integrated GPU",
                        "screen_size_inch": 13.6,
                        "battery_specs": "52.6Wh (Up to 18 Hours Battery Life)",
                        "color": "Midnight",
                        "trend_type": "spike",  # Price recently rose (WAIT verdict)
                        "listings": [
                            {
                                "store_slug": "amazon",
                                "external_product_id": "B0B3BQAIR2",
                                "product_url": "https://www.amazon.in/dp/B0B3BQAIR2",
                                "title_in_store": "Apple 2022 MacBook Air Laptop with M2 chip: 13.6-inch Liquid Retina Display, 8GB RAM, 256GB SSD Storage, Backlit Keyboard, Midnight",
                                "current_price": 94990.0,
                                "original_mrp": 99900.0,
                                "discount_percent": 5.0,
                                "rating_star": 4.7,
                                "rating_count": 14200,
                            },
                            {
                                "store_slug": "flipkart",
                                "external_product_id": "LPTAPLMBA2",
                                "product_url": "https://www.flipkart.com/apple-2022-macbook-air-m2-8-gb-256-gb-ssd/p/itmair2m2",
                                "title_in_store": "Apple MacBook AIR Apple M2 - (8 GB/256 GB SSD/macOS Monterey) MLY33HN/A (13.6 Inch, Midnight, 1.24 Kg)",
                                "current_price": 95900.0,
                                "original_mrp": 99900.0,
                                "discount_percent": 4.0,
                                "rating_star": 4.7,
                                "rating_count": 12800,
                            },
                            {
                                "store_slug": "croma",
                                "external_product_id": "CRM-256712",
                                "product_url": "https://www.croma.com/apple-macbook-air-m2-8gb-256gb/p/256712",
                                "title_in_store": "Apple MacBook Air 2022 M2 (13.6 Inch, 8GB, 256GB SSD, macOS, Midnight)",
                                "current_price": 96990.0,
                                "original_mrp": 99900.0,
                                "discount_percent": 3.0,
                                "rating_star": 4.8,
                                "rating_count": 3400,
                            },
                        ],
                    }
                ],
            },
            {
                "title": "ASUS Vivobook 15 (Intel Core i3 12th Gen)",
                "brand": "ASUS",
                "category": "laptop",
                "base_model": "Vivobook 15",
                "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=600&auto=format&fit=crop&q=80",
                "description": "Budget student and office laptop with 12th Gen Intel Core i3, 8GB RAM, 512GB NVMe SSD, and anti-glare FHD screen.",
                "variants": [
                    {
                        "variant_name": "8GB RAM / 512GB SSD / Intel Core i3 12th Gen / Quiet Blue",
                        "sku": "ASUS-VIVO15-8-512-BLU",
                        "ram_gb": 8,
                        "storage_gb": 512,
                        "cpu_processor": "Intel Core i3-1215U (6 Cores, Up to 4.4GHz)",
                        "gpu_graphics": "Intel UHD Graphics",
                        "screen_size_inch": 15.6,
                        "battery_specs": "42Wh (Up to 6 Hours Battery Life)",
                        "color": "Quiet Blue",
                        "trend_type": "normal",
                        "listings": [
                            {
                                "store_slug": "amazon",
                                "external_product_id": "B0BNNVASUS",
                                "product_url": "https://www.amazon.in/dp/B0BNNVASUS",
                                "title_in_store": "ASUS Vivobook 15, Intel Core i3-1215U 12th Gen, 15.6\" FHD Thin and Light Laptop (8GB/512GB SSD/Win 11/Office 2021/Blue/1.7 kg)",
                                "current_price": 36990.0,
                                "original_mrp": 49990.0,
                                "discount_percent": 26.0,
                                "rating_star": 4.1,
                                "rating_count": 3800,
                            },
                            {
                                "store_slug": "flipkart",
                                "external_product_id": "LPTASUSV15",
                                "product_url": "https://www.flipkart.com/asus-vivobook-15-core-i3-12th-gen/p/itmasusv15",
                                "title_in_store": "ASUS Vivobook 15 Intel Core i3 12th Gen 1215U - (8 GB/512 GB SSD/Windows 11 Home) X1502ZA-EJ321WS",
                                "current_price": 35990.0,
                                "original_mrp": 49990.0,
                                "discount_percent": 28.0,
                                "rating_star": 4.2,
                                "rating_count": 4200,
                            },
                        ],
                    }
                ],
            },

            # --------------------------- AUDIO / HEADPHONES ---------------------------
            {
                "title": "JBL Tune 770NC Wireless Over-Ear ANC Headphones",
                "brand": "JBL",
                "category": "audio",
                "base_model": "Tune 770NC",
                "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80",
                "description": "Wireless Active Noise Cancelling headphones with up to 70 hours battery life, Pure Bass sound, and multi-point Bluetooth connectivity.",
                "variants": [
                    {
                        "variant_name": "Over-Ear Wireless ANC / 70H Battery / Bluetooth 5.3 / Black",
                        "sku": "JBL-T770NC-BLK",
                        "ram_gb": None,
                        "storage_gb": None,
                        "cpu_processor": None,
                        "gpu_graphics": None,
                        "screen_size_inch": None,
                        "battery_specs": "70 Hours (Speed Charge: 5 mins = 3 hrs)",
                        "color": "Black",
                        "trend_type": "drop",
                        "listings": [
                            {
                                "store_slug": "amazon",
                                "external_product_id": "B0C7JBL770",
                                "product_url": "https://www.amazon.in/dp/B0C7JBL770",
                                "title_in_store": "JBL Tune 770NC Wireless Over Ear ANC Headphones with Mic, 70H Playtime, Multi-Point Connection, PureBass Sound (Black)",
                                "current_price": 5499.0,
                                "original_mrp": 7999.0,
                                "discount_percent": 31.0,
                                "rating_star": 4.3,
                                "rating_count": 11200,
                            },
                            {
                                "store_slug": "flipkart",
                                "external_product_id": "AUDJBL770NC",
                                "product_url": "https://www.flipkart.com/jbl-tune-770nc-anc-bluetooth-headset/p/itmjbl770nc",
                                "title_in_store": "JBL Tune 770NC with Active Noise Cancellation (ANC), 70 Hrs Playtime Bluetooth Headset (Black, On the Ear)",
                                "current_price": 5299.0,
                                "original_mrp": 7999.0,
                                "discount_percent": 33.7,
                                "rating_star": 4.2,
                                "rating_count": 9400,
                            },
                            {
                                "store_slug": "croma",
                                "external_product_id": "CRM-271890",
                                "product_url": "https://www.croma.com/jbl-tune-770nc-over-ear-bluetooth-headphone/p/271890",
                                "title_in_store": "JBL Tune 770NC Over-Ear Active Noise Cancellation Wireless Headphone (Adaptive Noise Cancelling, Black)",
                                "current_price": 5699.0,
                                "original_mrp": 7999.0,
                                "discount_percent": 28.7,
                                "rating_star": 4.4,
                                "rating_count": 2100,
                            },
                        ],
                    }
                ],
            },
            {
                "title": "Sony WH-1000XM5 Wireless Industry Leading Noise Canceling Headphones",
                "brand": "Sony",
                "category": "audio",
                "base_model": "WH-1000XM5",
                "image_url": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=600&auto=format&fit=crop&q=80",
                "description": "Flagship noise cancelling headphones with Auto NC Optimizer, 8 microphones, 30 hours battery life, and crystal-clear hands-free calling.",
                "variants": [
                    {
                        "variant_name": "Premium ANC / 30H Battery / Hi-Res LDAC / Silver",
                        "sku": "SNY-WH1000XM5-SLV",
                        "ram_gb": None,
                        "storage_gb": None,
                        "cpu_processor": None,
                        "gpu_graphics": None,
                        "screen_size_inch": None,
                        "battery_specs": "30 Hours (Quick Charge: 3 mins = 3 hrs)",
                        "color": "Silver",
                        "trend_type": "drop",
                        "listings": [
                            {
                                "store_slug": "amazon",
                                "external_product_id": "B09XS7JWH5",
                                "product_url": "https://www.amazon.in/dp/B09XS7JWH5",
                                "title_in_store": "Sony WH-1000XM5 Wireless Industry Leading Active Noise Cancelling Headphones, 8 Mics for Clear Calling, 30 Hr Battery (Silver)",
                                "current_price": 27990.0,
                                "original_mrp": 34990.0,
                                "discount_percent": 20.0,
                                "rating_star": 4.6,
                                "rating_count": 18900,
                            },
                            {
                                "store_slug": "flipkart",
                                "external_product_id": "AUDSNYXM5",
                                "product_url": "https://www.flipkart.com/sony-wh-1000xm5-bluetooth-headset/p/itmsnyxm5",
                                "title_in_store": "SONY WH-1000XM5 with 30 Hrs Playtime and Dual Processor Noise Canceling Bluetooth Headset (Silver)",
                                "current_price": 28490.0,
                                "original_mrp": 34990.0,
                                "discount_percent": 18.5,
                                "rating_star": 4.5,
                                "rating_count": 15200,
                            },
                        ],
                    }
                ],
            },

            # --------------------------- SMARTPHONES ---------------------------
            {
                "title": "OnePlus Nord CE4 5G (Snapdragon 7 Gen 3 / 100W SuperVOOC)",
                "brand": "OnePlus",
                "category": "smartphone",
                "base_model": "Nord CE4",
                "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=600&auto=format&fit=crop&q=80",
                "description": "5G smartphone featuring Snapdragon 7 Gen 3, 5500 mAh battery with 100W SuperVOOC fast charging, and 50MP Sony LYT-600 OIS camera.",
                "variants": [
                    {
                        "variant_name": "8GB RAM / 128GB Storage / Celadon Marble",
                        "sku": "1PL-NORDCE4-8-128-GRN",
                        "ram_gb": 8,
                        "storage_gb": 128,
                        "cpu_processor": "Qualcomm Snapdragon 7 Gen 3 (4nm)",
                        "gpu_graphics": "Adreno 720",
                        "screen_size_inch": 6.7,
                        "battery_specs": "5500 mAh (100W SuperVOOC Charge)",
                        "color": "Celadon Marble",
                        "trend_type": "normal",
                        "listings": [
                            {
                                "store_slug": "amazon",
                                "external_product_id": "B0CX9NORD4",
                                "product_url": "https://www.amazon.in/dp/B0CX9NORD4",
                                "title_in_store": "OnePlus Nord CE4 (Celadon Marble, 8GB RAM, 128GB Storage) | 100W SUPERVOOC | Snapdragon 7 Gen 3",
                                "current_price": 24999.0,
                                "original_mrp": 26999.0,
                                "discount_percent": 7.4,
                                "rating_star": 4.3,
                                "rating_count": 22000,
                            },
                            {
                                "store_slug": "flipkart",
                                "external_product_id": "MOB1PLCE4",
                                "product_url": "https://www.flipkart.com/oneplus-nord-ce4-celadon-marble-128-gb/p/itmce4",
                                "title_in_store": "OnePlus Nord CE4 (Celadon Marble, 128 GB) (8 GB RAM)",
                                "current_price": 24890.0,
                                "original_mrp": 26999.0,
                                "discount_percent": 7.8,
                                "rating_star": 4.3,
                                "rating_count": 19500,
                            },
                            {
                                "store_slug": "croma",
                                "external_product_id": "CRM-305910",
                                "product_url": "https://www.croma.com/oneplus-nord-ce4-5g-8gb-128gb/p/305910",
                                "title_in_store": "OnePlus Nord CE4 5G (8GB RAM, 128GB, Celadon Marble)",
                                "current_price": 24999.0,
                                "original_mrp": 26999.0,
                                "discount_percent": 7.4,
                                "rating_star": 4.4,
                                "rating_count": 5100,
                            },
                        ],
                    }
                ],
            },
            {
                "title": "Samsung Galaxy S23 FE 5G (8GB RAM / 128GB Storage)",
                "brand": "Samsung",
                "category": "smartphone",
                "base_model": "Galaxy S23 FE",
                "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02560?w=600&auto=format&fit=crop&q=80",
                "description": "Fan Edition flagship smartphone with Dynamic AMOLED 2X 120Hz display, Pro-grade 50MP Nightography camera, and IP68 water resistance.",
                "variants": [
                    {
                        "variant_name": "8GB RAM / 128GB Storage / Mint",
                        "sku": "SAM-S23FE-8-128-MNT",
                        "ram_gb": 8,
                        "storage_gb": 128,
                        "cpu_processor": "Samsung Exynos 2200 (4nm)",
                        "gpu_graphics": "Xclipse 920",
                        "screen_size_inch": 6.4,
                        "battery_specs": "4500 mAh (25W Fast Charge & Wireless Charging)",
                        "color": "Mint",
                        "trend_type": "drop",
                        "listings": [
                            {
                                "store_slug": "amazon",
                                "external_product_id": "B0CJ9S23FE",
                                "product_url": "https://www.amazon.in/dp/B0CJ9S23FE",
                                "title_in_store": "Samsung Galaxy S23 FE 5G (Mint, 8GB, 128GB Storage) | Dynamic AMOLED 2X | Pro-Grade Camera",
                                "current_price": 39999.0,
                                "original_mrp": 59999.0,
                                "discount_percent": 33.3,
                                "rating_star": 4.2,
                                "rating_count": 15400,
                            },
                            {
                                "store_slug": "flipkart",
                                "external_product_id": "MOBSAMS23FE",
                                "product_url": "https://www.flipkart.com/samsung-galaxy-s23-fe-mint-128-gb/p/itms23fe",
                                "title_in_store": "SAMSUNG Galaxy S23 FE (Mint, 128 GB) (8 GB RAM)",
                                "current_price": 38999.0,
                                "original_mrp": 59999.0,
                                "discount_percent": 35.0,
                                "rating_star": 4.2,
                                "rating_count": 16800,
                            },
                        ],
                    }
                ],
            },
        ]

        total_products = 0
        total_variants = 0
        total_listings = 0
        total_price_records = 0

        for item in catalog:
            # Create Canonical Product
            canonical = CanonicalProduct(
                title=item["title"],
                brand=item["brand"],
                category=item["category"],
                base_model=item["base_model"],
                image_url=item["image_url"],
                description=item["description"],
            )
            db.add(canonical)
            db.flush()
            total_products += 1

            for v_data in item["variants"]:
                variant = ProductVariant(
                    canonical_product_id=canonical.id,
                    variant_name=v_data["variant_name"],
                    sku=v_data["sku"],
                    ram_gb=v_data["ram_gb"],
                    storage_gb=v_data["storage_gb"],
                    cpu_processor=v_data["cpu_processor"],
                    gpu_graphics=v_data["gpu_graphics"],
                    screen_size_inch=v_data["screen_size_inch"],
                    battery_specs=v_data["battery_specs"],
                    color=v_data["color"],
                )
                db.add(variant)
                db.flush()
                total_variants += 1

                for l_data in v_data["listings"]:
                    store = store_objects[l_data["store_slug"]]
                    listing = StoreListing(
                        variant_id=variant.id,
                        store_id=store.id,
                        external_product_id=l_data["external_product_id"],
                        product_url=l_data["product_url"],
                        title_in_store=l_data["title_in_store"],
                        current_price=l_data["current_price"],
                        original_mrp=l_data["original_mrp"],
                        discount_percent=l_data["discount_percent"],
                        rating_star=l_data["rating_star"],
                        rating_count=l_data["rating_count"],
                        in_stock=True,
                    )
                    db.add(listing)
                    db.flush()
                    total_listings += 1

                    # Generate 90-day daily price logs for this store listing
                    history_points = generate_90_day_history(
                        current_price=l_data["current_price"],
                        base_mrp=l_data["original_mrp"],
                        trend_type=v_data.get("trend_type", "normal")
                    )

                    for rec_date, price_val in history_points:
                        ph = PriceHistoryRecord(
                            store_listing_id=listing.id,
                            price=price_val,
                            recorded_at=rec_date,
                        )
                        db.add(ph)
                        total_price_records += 1

        db.commit()
        print("\n[SUCCESS] Database seeding completed successfully!")
        print(f"   * Stores created: {len(store_objects)}")
        print(f"   * Canonical Products: {total_products}")
        print(f"   * Product Variants: {total_variants}")
        print(f"   * Store Listings: {total_listings} (Amazon, Flipkart, Croma)")
        print(f"   * Historical Price Points (90 Days): {total_price_records}")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
