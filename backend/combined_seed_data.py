import sqlite3
import json
from datetime import datetime
import random


def create_comprehensive_sample_data():
    """Create comprehensive sample data combining all seeding scripts with seller names"""

    print("🚀 Starting comprehensive database seeding...")

    # Connect to SQLite database
    conn = sqlite3.connect("listings.db")
    cursor = conn.cursor()

    # Seller names mapping - combining all sellers from all scripts
    seller_names = {
        "SELLER001": "TechGear Electronics",
        "SELLER002": "BookWise Publishing",
        "SELLER003": "MobileMax Accessories",
        "SELLER004": "HomeStyle Living",
        "SELLER005": "FitLife Sports",
        "SELLER006": "KitchenPro Essentials",
        "SELLER007": "StyleHub Fashion",
        "SELLER008": "AutoCare Solutions",
    }

    print(f"📊 Configured {len(seller_names)} sellers with names")

    # Comprehensive sample listings data (50+ entries with seller names included)
    sample_listings = [
        # Electronics - Computers & Accessories (SELLER001 - TechGear Electronics)
        {
            "seller_id": "SELLER001",
            "seller_name": seller_names["SELLER001"],
            "sku": "LAPTOP-001",
            "title": "High Performance Gaming Laptop",
            "description": "Powerful gaming laptop with RTX graphics and fast processor",
            "price": 1299.99,
            "quantity": 25,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER", "A2EUQ1WTGCTBG2"]),
        },
        {
            "seller_id": "SELLER001",
            "seller_name": seller_names["SELLER001"],
            "sku": "LAPTOP-002",
            "title": "Business Ultrabook 14-inch",
            "description": "Lightweight business laptop with long battery life",
            "price": 899.99,
            "quantity": 40,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER"]),
        },
        {
            "seller_id": "SELLER001",
            "seller_name": seller_names["SELLER001"],
            "sku": "LAPTOP-003",
            "title": "Budget Student Laptop",
            "description": "Affordable laptop perfect for students and basic tasks",
            "price": 449.99,
            "quantity": 60,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER", "A1AM78C64UM0Y8"]),
        },
        {
            "seller_id": "SELLER001",
            "seller_name": seller_names["SELLER001"],
            "sku": "MOUSE-001",
            "title": "Wireless Gaming Mouse",
            "description": "Ergonomic wireless mouse with RGB lighting",
            "price": 79.99,
            "quantity": 150,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER"]),
        },
        {
            "seller_id": "SELLER001",
            "seller_name": seller_names["SELLER001"],
            "sku": "MOUSE-002",
            "title": "Bluetooth Office Mouse",
            "description": "Silent click wireless mouse for office use",
            "price": 29.99,
            "quantity": 200,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER", "A2EUQ1WTGCTBG2"]),
        },
        {
            "seller_id": "SELLER001",
            "seller_name": seller_names["SELLER001"],
            "sku": "KEYBOARD-001",
            "title": "Mechanical Gaming Keyboard",
            "description": "RGB backlit mechanical keyboard with blue switches",
            "price": 129.99,
            "quantity": 75,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER", "A1AM78C64UM0Y8"]),
        },
        {
            "seller_id": "SELLER001",
            "seller_name": seller_names["SELLER001"],
            "sku": "KEYBOARD-002",
            "title": "Wireless Compact Keyboard",
            "description": "Slim wireless keyboard with numeric keypad",
            "price": 59.99,
            "quantity": 90,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER"]),
        },
        {
            "seller_id": "SELLER001",
            "seller_name": seller_names["SELLER001"],
            "sku": "MONITOR-001",
            "title": "27-inch 4K Gaming Monitor",
            "description": "Ultra HD gaming monitor with 144Hz refresh rate",
            "price": 399.99,
            "quantity": 30,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER"]),
        },
        {
            "seller_id": "SELLER001",
            "seller_name": seller_names["SELLER001"],
            "sku": "MONITOR-002",
            "title": "24-inch Office Monitor",
            "description": "Full HD monitor perfect for office work",
            "price": 179.99,
            "quantity": 45,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER", "A2EUQ1WTGCTBG2"]),
        },
        {
            "seller_id": "SELLER001",
            "seller_name": seller_names["SELLER001"],
            "sku": "HEADSET-001",
            "title": "Gaming Headset with Microphone",
            "description": "Professional gaming headset with noise-canceling microphone",
            "price": 89.99,
            "quantity": 60,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER"]),
        },
        {
            "seller_id": "SELLER001",
            "seller_name": seller_names["SELLER001"],
            "sku": "WEBCAM-001",
            "title": "1080p HD Webcam",
            "description": "High definition webcam for video calls and streaming",
            "price": 69.99,
            "quantity": 80,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER"]),
        },
        {
            "seller_id": "SELLER001",
            "seller_name": seller_names["SELLER001"],
            "sku": "SPEAKER-001",
            "title": "Bluetooth Desktop Speakers",
            "description": "Compact wireless speakers with rich sound",
            "price": 49.99,
            "quantity": 100,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER", "A2EUQ1WTGCTBG2"]),
        },
        # Books & Education (SELLER002 - BookWise Publishing)
        {
            "seller_id": "SELLER002",
            "seller_name": seller_names["SELLER002"],
            "sku": "BOOK-001",
            "title": "Python Programming Guide",
            "description": "Complete guide to Python programming for beginners",
            "price": 29.99,
            "quantity": 200,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER"]),
        },
        {
            "seller_id": "SELLER002",
            "seller_name": seller_names["SELLER002"],
            "sku": "BOOK-002",
            "title": "Web Development with FastAPI",
            "description": "Learn modern web development using FastAPI framework",
            "price": 39.99,
            "quantity": 100,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER", "A2EUQ1WTGCTBG2"]),
        },
        {
            "seller_id": "SELLER002",
            "seller_name": seller_names["SELLER002"],
            "sku": "BOOK-003",
            "title": "Machine Learning Fundamentals",
            "description": "Introduction to machine learning concepts and algorithms",
            "price": 49.99,
            "quantity": 150,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER"]),
        },
        {
            "seller_id": "SELLER002",
            "seller_name": seller_names["SELLER002"],
            "sku": "BOOK-004",
            "title": "Data Science with Python",
            "description": "Comprehensive guide to data science using Python",
            "price": 44.99,
            "quantity": 120,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER", "A1AM78C64UM0Y8"]),
        },
        {
            "seller_id": "SELLER002",
            "seller_name": seller_names["SELLER002"],
            "sku": "BOOK-005",
            "title": "JavaScript: The Complete Guide",
            "description": "Master JavaScript from basics to advanced concepts",
            "price": 34.99,
            "quantity": 180,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER"]),
        },
        {
            "seller_id": "SELLER002",
            "seller_name": seller_names["SELLER002"],
            "sku": "TABLET-001",
            "title": "Drawing Tablet for Artists",
            "description": "Professional drawing tablet with pressure-sensitive stylus",
            "price": 199.99,
            "quantity": 30,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER", "A1AM78C64UM0Y8"]),
        },
        {
            "seller_id": "SELLER002",
            "seller_name": seller_names["SELLER002"],
            "sku": "TABLET-002",
            "title": "10-inch Android Tablet",
            "description": "High-performance Android tablet for entertainment and work",
            "price": 299.99,
            "quantity": 50,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER"]),
        },
        {
            "seller_id": "SELLER002",
            "seller_name": seller_names["SELLER002"],
            "sku": "EBOOK-001",
            "title": "Digital Marketing Mastery",
            "description": "Complete digital marketing course and strategies",
            "price": 19.99,
            "quantity": 500,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER", "A2EUQ1WTGCTBG2"]),
        },
        # Mobile & Electronics (SELLER003 - MobileMax Accessories)
        {
            "seller_id": "SELLER003",
            "seller_name": seller_names["SELLER003"],
            "sku": "PHONE-001",
            "title": "Smartphone Case - Clear",
            "description": "Transparent protective case for smartphones",
            "price": 19.99,
            "quantity": 500,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER"]),
        },
        {
            "seller_id": "SELLER003",
            "seller_name": seller_names["SELLER003"],
            "sku": "PHONE-002",
            "title": "Wireless Charger Pad",
            "description": "Fast wireless charging pad compatible with all Qi devices",
            "price": 49.99,
            "quantity": 80,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER", "A2EUQ1WTGCTBG2"]),
        },
        {
            "seller_id": "SELLER003",
            "seller_name": seller_names["SELLER003"],
            "sku": "PHONE-003",
            "title": "Phone Stand Adjustable",
            "description": "Adjustable phone stand for desk and bedside use",
            "price": 15.99,
            "quantity": 300,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER"]),
        },
        {
            "seller_id": "SELLER003",
            "seller_name": seller_names["SELLER003"],
            "sku": "CABLE-001",
            "title": "USB-C to USB-A Cable",
            "description": "High-speed data transfer cable, 6 feet length",
            "price": 12.99,
            "quantity": 1000,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER"]),
        },
        {
            "seller_id": "SELLER003",
            "seller_name": seller_names["SELLER003"],
            "sku": "CABLE-002",
            "title": "Lightning to USB Cable",
            "description": "MFi certified lightning cable for Apple devices",
            "price": 24.99,
            "quantity": 400,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER", "A2EUQ1WTGCTBG2"]),
        },
        {
            "seller_id": "SELLER003",
            "seller_name": seller_names["SELLER003"],
            "sku": "POWERBANK-001",
            "title": "10000mAh Portable Power Bank",
            "description": "High capacity power bank with fast charging",
            "price": 39.99,
            "quantity": 150,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER"]),
        },
        {
            "seller_id": "SELLER003",
            "seller_name": seller_names["SELLER003"],
            "sku": "EARBUDS-001",
            "title": "Wireless Bluetooth Earbuds",
            "description": "True wireless earbuds with charging case",
            "price": 79.99,
            "quantity": 120,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER", "A1AM78C64UM0Y8"]),
        },
        # Home & Garden (SELLER004 - HomeStyle Living)
        {
            "seller_id": "SELLER004",
            "seller_name": seller_names["SELLER004"],
            "sku": "LAMP-001",
            "title": "LED Desk Lamp with USB Charging",
            "description": "Adjustable LED desk lamp with built-in USB ports",
            "price": 45.99,
            "quantity": 80,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER"]),
        },
        {
            "seller_id": "SELLER004",
            "seller_name": seller_names["SELLER004"],
            "sku": "PLANT-001",
            "title": "Indoor Plant Pot Set",
            "description": "Set of 3 ceramic plant pots with drainage",
            "price": 29.99,
            "quantity": 100,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER", "A2EUQ1WTGCTBG2"]),
        },
        {
            "seller_id": "SELLER004",
            "seller_name": seller_names["SELLER004"],
            "sku": "ORGANIZER-001",
            "title": "Desk Organizer with Drawers",
            "description": "Wooden desk organizer with multiple compartments",
            "price": 34.99,
            "quantity": 60,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER"]),
        },
        {
            "seller_id": "SELLER004",
            "seller_name": seller_names["SELLER004"],
            "sku": "CUSHION-001",
            "title": "Memory Foam Seat Cushion",
            "description": "Ergonomic memory foam cushion for office chairs",
            "price": 39.99,
            "quantity": 90,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER"]),
        },
        {
            "seller_id": "SELLER004",
            "seller_name": seller_names["SELLER004"],
            "sku": "MIRROR-001",
            "title": "LED Vanity Mirror",
            "description": "Hollywood style LED vanity mirror with dimmer",
            "price": 89.99,
            "quantity": 40,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER", "A2EUQ1WTGCTBG2"]),
        },
        # Sports & Fitness (SELLER005 - FitLife Sports)
        {
            "seller_id": "SELLER005",
            "seller_name": seller_names["SELLER005"],
            "sku": "YOGA-001",
            "title": "Premium Yoga Mat",
            "description": "Non-slip yoga mat with carrying strap",
            "price": 29.99,
            "quantity": 150,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER"]),
        },
        {
            "seller_id": "SELLER005",
            "seller_name": seller_names["SELLER005"],
            "sku": "WEIGHTS-001",
            "title": "Adjustable Dumbbell Set",
            "description": "Space-saving adjustable dumbbells 5-50 lbs",
            "price": 199.99,
            "quantity": 25,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER"]),
        },
        {
            "seller_id": "SELLER005",
            "seller_name": seller_names["SELLER005"],
            "sku": "BOTTLE-001",
            "title": "Insulated Water Bottle",
            "description": "Stainless steel water bottle keeps drinks cold 24hrs",
            "price": 24.99,
            "quantity": 200,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER", "A2EUQ1WTGCTBG2"]),
        },
        {
            "seller_id": "SELLER005",
            "seller_name": seller_names["SELLER005"],
            "sku": "BAND-001",
            "title": "Resistance Band Set",
            "description": "Set of 5 resistance bands with door anchor",
            "price": 19.99,
            "quantity": 180,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER"]),
        },
        {
            "seller_id": "SELLER005",
            "seller_name": seller_names["SELLER005"],
            "sku": "TRACKER-001",
            "title": "Fitness Activity Tracker",
            "description": "Waterproof fitness tracker with heart rate monitor",
            "price": 79.99,
            "quantity": 70,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER", "A1AM78C64UM0Y8"]),
        },
        # Kitchen & Dining (SELLER006 - KitchenPro Essentials)
        {
            "seller_id": "SELLER006",
            "seller_name": seller_names["SELLER006"],
            "sku": "BLENDER-001",
            "title": "High-Speed Blender",
            "description": "Professional grade blender for smoothies and soups",
            "price": 149.99,
            "quantity": 35,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER"]),
        },
        {
            "seller_id": "SELLER006",
            "seller_name": seller_names["SELLER006"],
            "sku": "KNIFE-001",
            "title": "Chef Knife Set",
            "description": "Professional 8-piece chef knife set with block",
            "price": 89.99,
            "quantity": 50,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER", "A2EUQ1WTGCTBG2"]),
        },
        {
            "seller_id": "SELLER006",
            "seller_name": seller_names["SELLER006"],
            "sku": "COFFEE-001",
            "title": "French Press Coffee Maker",
            "description": "Borosilicate glass French press, 34oz capacity",
            "price": 34.99,
            "quantity": 80,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER"]),
        },
        {
            "seller_id": "SELLER006",
            "seller_name": seller_names["SELLER006"],
            "sku": "SCALE-001",
            "title": "Digital Kitchen Scale",
            "description": "Precision digital scale for cooking and baking",
            "price": 25.99,
            "quantity": 120,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER"]),
        },
        {
            "seller_id": "SELLER006",
            "seller_name": seller_names["SELLER006"],
            "sku": "CONTAINER-001",
            "title": "Glass Food Storage Set",
            "description": "Set of 10 glass containers with airtight lids",
            "price": 49.99,
            "quantity": 90,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER", "A2EUQ1WTGCTBG2"]),
        },
        # Fashion & Accessories (SELLER007 - StyleHub Fashion)
        {
            "seller_id": "SELLER007",
            "seller_name": seller_names["SELLER007"],
            "sku": "WATCH-001",
            "title": "Smartwatch with GPS",
            "description": "Fitness smartwatch with GPS and heart rate monitoring",
            "price": 199.99,
            "quantity": 45,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER"]),
        },
        {
            "seller_id": "SELLER007",
            "seller_name": seller_names["SELLER007"],
            "sku": "WALLET-001",
            "title": "RFID Blocking Wallet",
            "description": "Slim leather wallet with RFID protection",
            "price": 39.99,
            "quantity": 100,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER", "A2EUQ1WTGCTBG2"]),
        },
        {
            "seller_id": "SELLER007",
            "seller_name": seller_names["SELLER007"],
            "sku": "SUNGLASSES-001",
            "title": "Polarized Sunglasses",
            "description": "UV protection polarized sunglasses with case",
            "price": 49.99,
            "quantity": 80,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER"]),
        },
        {
            "seller_id": "SELLER007",
            "seller_name": seller_names["SELLER007"],
            "sku": "BAG-001",
            "title": "Laptop Backpack",
            "description": "Water-resistant laptop backpack with USB charging port",
            "price": 59.99,
            "quantity": 70,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER", "A1AM78C64UM0Y8"]),
        },
        {
            "seller_id": "SELLER007",
            "seller_name": seller_names["SELLER007"],
            "sku": "BELT-001",
            "title": "Leather Belt Set",
            "description": "Reversible leather belt black and brown",
            "price": 29.99,
            "quantity": 150,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER"]),
        },
        # Automotive (SELLER008 - AutoCare Solutions)
        {
            "seller_id": "SELLER008",
            "seller_name": seller_names["SELLER008"],
            "sku": "MOUNT-001",
            "title": "Car Phone Mount",
            "description": "Magnetic car phone mount for dashboard",
            "price": 19.99,
            "quantity": 200,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER"]),
        },
        {
            "seller_id": "SELLER008",
            "seller_name": seller_names["SELLER008"],
            "sku": "CHARGER-001",
            "title": "Car USB Charger",
            "description": "Dual USB car charger with fast charging",
            "price": 14.99,
            "quantity": 300,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER", "A2EUQ1WTGCTBG2"]),
        },
        {
            "seller_id": "SELLER008",
            "seller_name": seller_names["SELLER008"],
            "sku": "ORGANIZER-002",
            "title": "Car Trunk Organizer",
            "description": "Collapsible car trunk organizer with compartments",
            "price": 34.99,
            "quantity": 80,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER"]),
        },
        {
            "seller_id": "SELLER008",
            "seller_name": seller_names["SELLER008"],
            "sku": "COVER-001",
            "title": "Car Seat Covers Set",
            "description": "Universal fit car seat covers, waterproof",
            "price": 79.99,
            "quantity": 40,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER"]),
        },
        {
            "seller_id": "SELLER008",
            "seller_name": seller_names["SELLER008"],
            "sku": "VACUUM-001",
            "title": "Car Vacuum Cleaner",
            "description": "Portable car vacuum with multiple attachments",
            "price": 49.99,
            "quantity": 60,
            "status": "ACTIVE",
            "marketplace_ids": json.dumps(["ATVPDKIKX0DER", "A1AM78C64UM0Y8"]),
        },
    ]

    print(f"📦 Prepared {len(sample_listings)} comprehensive sample listings")

    # Clear existing data for fresh start
    print("🧹 Clearing existing data...")
    cursor.execute("DELETE FROM listings_items")

    # Insert comprehensive sample data with seller names included
    print("💾 Inserting comprehensive sample data...")
    inserted_count = 0

    for listing in sample_listings:
        try:
            cursor.execute(
                """
                INSERT INTO listings_items 
                (seller_id, seller_name, sku, title, description, price, quantity, status, marketplace_ids, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    listing["seller_id"],
                    listing["seller_name"],
                    listing["sku"],
                    listing["title"],
                    listing["description"],
                    listing["price"],
                    listing["quantity"],
                    listing["status"],
                    listing["marketplace_ids"],
                    datetime.now(),
                    datetime.now(),
                ),
            )
            inserted_count += 1
        except Exception as e:
            print(f"❌ Error inserting {listing['sku']}: {e}")

    conn.commit()

    # Verify and display comprehensive statistics
    print("\n📊 Verifying data insertion...")

    # Count by seller
    cursor.execute(
        "SELECT seller_id, seller_name, COUNT(*) FROM listings_items GROUP BY seller_id, seller_name ORDER BY seller_id"
    )
    seller_stats = cursor.fetchall()

    # Count by status
    cursor.execute("SELECT status, COUNT(*) FROM listings_items GROUP BY status")
    status_stats = cursor.fetchall()

    # Price range
    cursor.execute("SELECT MIN(price), MAX(price), AVG(price) FROM listings_items")
    price_stats = cursor.fetchone()

    # Total quantity
    cursor.execute("SELECT SUM(quantity) FROM listings_items")
    total_quantity = cursor.fetchone()[0]

    conn.close()

    # Display comprehensive results
    print(f"\n✅ Successfully inserted {inserted_count} comprehensive sample listings!")

    print(f"\n📈 COMPREHENSIVE DATABASE STATISTICS:")
    print(f"{'='*60}")

    print(f"\n🏪 SELLERS ({len(seller_stats)} total):")
    for seller_id, seller_name, count in seller_stats:
        print(f"  • {seller_id}: {seller_name} ({count} listings)")

    print(f"\n📊 STATUS DISTRIBUTION:")
    for status, count in status_stats:
        print(f"  • {status}: {count} listings")

    print(f"\n💰 PRICING STATISTICS:")
    print(f"  • Price Range: ${price_stats[0]:.2f} - ${price_stats[1]:.2f}")
    print(f"  • Average Price: ${price_stats[2]:.2f}")
    print(f"  • Total Inventory: {total_quantity:,} units")

    print(f"\n🎯 PRODUCT CATEGORIES:")
    print(f"  • Electronics & Computers (TechGear Electronics)")
    print(f"  • Books & Education (BookWise Publishing)")
    print(f"  • Mobile & Electronics (MobileMax Accessories)")
    print(f"  • Home & Garden (HomeStyle Living)")
    print(f"  • Sports & Fitness (FitLife Sports)")
    print(f"  • Kitchen & Dining (KitchenPro Essentials)")
    print(f"  • Fashion & Accessories (StyleHub Fashion)")
    print(f"  • Automotive (AutoCare Solutions)")

    print(f"\n🌍 MARKETPLACE COVERAGE:")
    print(f"  • US Marketplace (ATVPDKIKX0DER)")
    print(f"  • Canada Marketplace (A2EUQ1WTGCTBG2)")
    print(f"  • Mexico Marketplace (A1AM78C64UM0Y8)")

    print(f"\n🎉 COMPREHENSIVE SEEDING COMPLETED!")
    print(f"Database is ready for testing with realistic sample data.")


if __name__ == "__main__":
    create_comprehensive_sample_data()
