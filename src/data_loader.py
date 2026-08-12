"""
ShopPulse - E-Commerce Dataset Generator & Ingestion Module
Generates a realistic, enterprise-grade e-commerce transaction dataset with 12,000+ orders,
seasonal trends, pricing elasticity, customer segmentation, and geographical distribution.
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Set deterministic seed for reproducibility
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# Catalog definitions
PRODUCT_CATALOG = {
    "Technology": {
        "subcategories": ["Laptops", "Smartphones", "Accessories", "Monitors", "Audio"],
        "base_price_range": (35.0, 1850.0),
        "margin_range": (0.18, 0.42),
        "discount_max": 0.25,
        "items": [
            ("ProBook Ultra 15 Laptop", 1250.00, 820.00),
            ("Zenith 14-inch OLED Laptop", 1450.00, 960.00),
            ("OctaCore Gaming Desktop", 1750.00, 1180.00),
            ("Nova X Smartphone 256GB", 899.00, 580.00),
            ("Aero Lite 5G Phone", 499.00, 310.00),
            ("VividColor 27-inch 4K Monitor", 380.00, 240.00),
            ("UltraWide 34-inch Curved Display", 650.00, 420.00),
            ("Noise-Cancelling Wireless Headphones", 249.00, 130.00),
            ("TrueWireless Earbuds Pro", 129.00, 65.00),
            ("Ergonomic Mechanical Keyboard", 119.00, 55.00),
            ("Precision Wireless Laser Mouse", 59.00, 24.00),
            ("Thunderbolt 4 Multi-Port Dock", 189.00, 95.00),
            ("FastCharge 65W GaN Wall Charger", 39.00, 14.00),
            ("External NVMe SSD 1TB", 109.00, 58.00),
            ("Smart Watch Series 7 Titanium", 399.00, 220.00),
            ("Fitness Tracker Band 5", 69.00, 32.00),
            ("1080p Streamer Pro Webcam", 89.00, 42.00),
            ("Studio USB Condenser Microphone", 129.00, 62.00),
            ("Wi-Fi 6 Mesh Router System (3-Pack)", 279.00, 160.00),
            ("Portable Power Bank 20000mAh", 49.00, 21.00),
        ]
    },
    "Furniture": {
        "subcategories": ["Chairs", "Desks", "Bookcases", "Storage", "Lighting"],
        "base_price_range": (45.0, 980.0),
        "margin_range": (0.12, 0.35),
        "discount_max": 0.30,
        "items": [
            ("ErgoExecutive Mesh Chair", 349.00, 210.00),
            ("High-Back Leather Office Chair", 289.00, 175.00),
            ("Dual-Motor Electric Standing Desk", 599.00, 390.00),
            ("Solid Oak Minimalist Desk 60-inch", 449.00, 280.00),
            ("5-Tier Industrial Bookcase", 189.00, 115.00),
            ("Modern 3-Drawer Filing Cabinet", 159.00, 95.00),
            ("Architect LED Desk Task Lamp", 79.00, 38.00),
            ("Acoustic Office Room Divider", 229.00, 140.00),
            ("Memory Foam Footrest Cushion", 45.00, 18.00),
            ("Heavy Duty Monitor Arm Dual Mount", 119.00, 62.00),
            ("Solid Pine Coffee Table", 210.00, 130.00),
            ("Accent Velvet Armchair", 380.00, 230.00),
            ("Modular Storage Cube Organizer", 95.00, 52.00),
            ("Adjustable Drafting Stool", 139.00, 82.00),
            ("Mid-Century Credenza Sideboard", 750.00, 480.00),
        ]
    },
    "Office Supplies": {
        "subcategories": ["Paper", "Binders", "Writing", "Organizers", "Envelopes"],
        "base_price_range": (8.0, 120.0),
        "margin_range": (0.28, 0.55),
        "discount_max": 0.20,
        "items": [
            ("Premium Multipurpose Copy Paper (5 Reams)", 42.00, 20.00),
            ("Heavy Duty 3-Ring Presentation Binders (Pack of 6)", 28.00, 12.00),
            ("Gel Ink Pen Set (0.7mm, 24-Pack)", 19.50, 7.50),
            ("Executive Leather Hardcover Notebook", 24.00, 9.00),
            ("Self-Adhesive Sticky Notes Bulk Pack", 14.00, 5.00),
            ("Cross-Cut Confidential Paper Shredder", 89.00, 48.00),
            ("Heavy-Duty Desktop Stapler & Remover", 22.00, 8.50),
            ("Mesh Desk Organizer Set (5 Pieces)", 34.00, 14.00),
            ("Expanding File Folder 13 Pockets", 16.00, 6.00),
            ("Laminator Machine with Pouches", 58.00, 28.00),
            ("Dry Erase Magnetic Whiteboard 36x24", 65.00, 31.00),
            ("Assorted Binder Clips & Paper Clips Tub", 12.00, 4.00),
            ("Padded Bubble Mailers #2 (Box of 50)", 32.00, 13.00),
            ("Permanent Markers Chisel Tip (12-Pack)", 15.00, 5.50),
            ("Thermal Shipping Label Printer", 129.00, 72.00),
        ]
    },
    "Apparel": {
        "subcategories": ["Outerwear", "Footwear", "Activewear", "Accessories", "Casual"],
        "base_price_range": (20.0, 320.0),
        "margin_range": (0.35, 0.65),
        "discount_max": 0.40,
        "items": [
            ("All-Weather Waterproof Shell Jacket", 189.00, 80.00),
            ("Merino Wool Thermal Sweater", 119.00, 45.00),
            ("Breathable Running Sneakers", 129.00, 52.00),
            ("Casual Canvas Low-Top Shoes", 65.00, 26.00),
            ("Performance Compression Leggings", 48.00, 16.00),
            ("Quick-Dry Athletic Training Shirt", 32.00, 11.00),
            ("Classic Oxford Button-Down Shirt", 55.00, 20.00),
            ("Comfort Stretch Denim Jeans", 78.00, 28.00),
            ("Polarized UV400 Sunglasses", 85.00, 24.00),
            ("Genuine Leather Dress Belt", 42.00, 14.00),
            ("Water-Resistant Commuter Backpack", 95.00, 36.00),
            ("Thermal Fleece Zip Hoodie", 62.00, 22.00),
            ("Seamless Sports Bra High Impact", 38.00, 13.00),
            ("Waterproof Hiking Boots", 165.00, 68.00),
            ("Cashmere Knit Winter Beanie", 39.00, 12.00),
        ]
    },
    "Home & Kitchen": {
        "subcategories": ["Appliances", "Cookware", "Dining", "Storage", "Coffee"],
        "base_price_range": (25.0, 450.0),
        "margin_range": (0.22, 0.48),
        "discount_max": 0.30,
        "items": [
            ("Espresso Machine with Milk Frother", 349.00, 195.00),
            ("Conical Burr Coffee Grinder", 99.00, 52.00),
            ("Digital Air Fryer XL 6-Quart", 129.00, 68.00),
            ("Stainless Steel Cookware Set (10-Piece)", 289.00, 150.00),
            ("Cast Iron Enameled Dutch Oven 6-Quart", 119.00, 58.00),
            ("Professional High-Speed Blender 1200W", 179.00, 92.00),
            ("Chef's Knife Japanese Damascus Steel 8-inch", 89.00, 38.00),
            ("Smart Electric Kettle Temperature Control", 69.00, 33.00),
            ("Airtight Food Storage Containers (Set of 12)", 45.00, 19.00),
            ("Robot Vacuum Cleaner with Mapping", 299.00, 165.00),
            ("HEPA Air Purifier for Large Rooms", 169.00, 88.00),
            ("Porcelain Dinnerware Set 16-Piece", 79.00, 36.00),
            ("Vacuum Insulated Thermal Carafe 2L", 34.00, 14.00),
            ("Digital Touch Kitchen Food Scale", 24.00, 9.50),
            ("Bamboo Cutting Board 3-Piece Set", 32.00, 12.00),
        ]
    }
}

REGIONAL_CITIES = {
    "North": ["New York", "Chicago", "Boston", "Philadelphia", "Detroit", "Minneapolis"],
    "South": ["Houston", "Atlanta", "Miami", "Dallas", "Austin", "Charlotte"],
    "East": ["Washington D.C.", "Baltimore", "Pittsburgh", "Newark", "Buffalo"],
    "West": ["Los Angeles", "San Francisco", "Seattle", "Denver", "Phoenix", "San Diego"]
}

CUSTOMER_SEGMENTS = ["Consumer", "Corporate", "Home Office", "Small Business"]
PAYMENT_METHODS = ["Credit Card", "PayPal", "Debit Card", "UPI / Net Banking"]

FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda",
    "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
    "Kenneth", "Dorothy", "Kevin", "Carol", "Brian", "Amanda", "George", "Melissa",
    "Edward", "Deborah", "Ronald", "Stephanie", "Timothy", "Rebecca", "Jason", "Sharon",
    "Jeffrey", "Laura", "Ryan", "Cynthia", "Jacob", "Kathleen", "Gary", "Amy",
    "Nicholas", "Angela", "Eric", "Shirley", "Jonathan", "Anna", "Stephen", "Brenda",
    "Larry", "Pamela", "Justin", "Emma", "Scott", "Nicole", "Brandon", "Helen",
    "Benjamin", "Samantha", "Samuel", "Katherine", "Gregory", "Christine", "Alexander", "Debra",
    "Frank", "Rachel", "Patrick", "Carolyn", "Raymond", "Janet", "Jack", "Catherine",
    "Dennis", "Maria", "Jerry", "Heather", "Tyler", "Diane", "Aaron", "Ruth"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill",
    "Flores", "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell",
    "Mitchell", "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz",
    "Parker", "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales",
    "Murphy", "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson",
    "Bailey", "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward",
    "Richardson", "Watson", "Brooks", "Chavez", "Wood", "James", "Bennett", "Gray",
    "Mendoza", "Ruiz", "Hughes", "Price", "Alvarez", "Castillo", "Sanders", "Patel",
    "Myers", "Long", "Ross", "Foster", "Jimenez", "Powell", "Jenkins", "Perry"
]

def generate_customer_pool(num_customers: int = 2400) -> list:
    """Generate a realistic pool of unique customers with segment, location, and behavior traits."""
    customers = []
    for i in range(1, num_customers + 1):
        cust_id = f"CUST-{1000 + i}"
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        name = f"{fn} {ln}"
        
        segment_weights = [0.48, 0.28, 0.14, 0.10]
        segment = np.random.choice(CUSTOMER_SEGMENTS, p=segment_weights)
        
        region = random.choice(list(REGIONAL_CITIES.keys()))
        city = random.choice(REGIONAL_CITIES[region])
        preferred_payment = np.random.choice(PAYMENT_METHODS, p=[0.42, 0.28, 0.18, 0.12])
        
        # Inherent customer propensity to purchase (VIP vs casual)
        activity_weight = np.random.exponential(scale=1.0)
        
        customers.append({
            "customer_id": cust_id,
            "customer_name": name,
            "customer_segment": segment,
            "region": region,
            "city": city,
            "preferred_payment": preferred_payment,
            "activity_weight": max(0.2, min(activity_weight, 5.0))
        })
    return customers

def build_product_master() -> list:
    """Expand product list to 500+ distinct SKUs with realistic unit prices and costs."""
    products = []
    sku_counter = 100
    
    for category, cat_data in PRODUCT_CATALOG.items():
        base_items = cat_data["items"]
        subcategories = cat_data["subcategories"]
        
        for item_name, base_price, base_cost in base_items:
            # Create base product
            sku_counter += 1
            prod_id = f"PROD-{sku_counter}"
            subcat = random.choice(subcategories)
            products.append({
                "product_id": prod_id,
                "product_name": item_name,
                "category": category,
                "subcategory": subcat,
                "unit_price": round(base_price, 2),
                "cost": round(base_cost, 2),
                "discount_max": cat_data["discount_max"]
            })
            
            # Create realistic variations (models, sizes, editions) to reach 500+ SKUs
            variants = [
                ("Plus Edition", 1.18, 1.15),
                ("Pro Max Edition", 1.35, 1.30),
                ("Compact / Slim", 0.85, 0.82),
                ("Studio Bundle", 1.50, 1.45),
                ("Eco-Friendly Series", 1.08, 1.05),
                ("Enterprise Fleet", 1.25, 1.20),
                ("Special Edition Matte Black", 1.12, 1.08),
            ]
            for var_suffix, price_mult, cost_mult in variants:
                sku_counter += 1
                var_prod_id = f"PROD-{sku_counter}"
                var_name = f"{item_name} - {var_suffix}"
                products.append({
                    "product_id": var_prod_id,
                    "product_name": var_name,
                    "category": category,
                    "subcategory": subcat,
                    "unit_price": round(base_price * price_mult, 2),
                    "cost": round(base_cost * cost_mult, 2),
                    "discount_max": cat_data["discount_max"]
                })
                
    return products

def generate_synthetic_dataset(
    target_records: int = 12500,
    start_date: str = "2024-01-01",
    end_date: str = "2025-06-30"
) -> pd.DataFrame:
    """
    Generate comprehensive e-commerce transaction dataset with realistic
    seasonality, price-volume elasticity, customer retention cohorts, and margins.
    """
    customers = generate_customer_pool(num_customers=2400)
    products = build_product_master()
    
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    total_days = (end_dt - start_dt).days
    
    customer_weights = np.array([c["activity_weight"] for c in customers])
    customer_weights /= customer_weights.sum()
    
    rows = []
    order_id_counter = 100001
    
    # Pre-generate dates with seasonality (Q4 bump, Black Friday surge, weekend surge)
    day_weights = []
    for day_offset in range(total_days):
        current_date = start_dt + timedelta(days=day_offset)
        month = current_date.month
        weekday = current_date.weekday()
        
        weight = 1.0
        # Holiday seasonality (Oct, Nov, Dec)
        if month in [11, 12]:
            weight *= 1.75
        elif month in [10, 1]:
            weight *= 1.25
        elif month in [6, 7]: # Summer sale
            weight *= 1.15
        elif month in [2, 3]: # Post-holiday lull
            weight *= 0.85
            
        # Weekend boost (Friday, Saturday, Sunday)
        if weekday in [4, 5, 6]:
            weight *= 1.20
            
        day_weights.append(weight)
        
    day_weights = np.array(day_weights) / sum(day_weights)
    
    # Category popularity weights
    cat_weights = {
        "Technology": 0.28,
        "Furniture": 0.20,
        "Office Supplies": 0.24,
        "Apparel": 0.16,
        "Home & Kitchen": 0.12
    }
    
    prod_weights = []
    for p in products:
        base_cat_w = cat_weights.get(p["category"], 0.2)
        # Higher priced items have slightly lower volume
        price_factor = 1.0 / (1.0 + np.log1p(p["unit_price"] / 50.0))
        prod_weights.append(base_cat_w * price_factor)
        
    prod_weights = np.array(prod_weights) / sum(prod_weights)
    
    for _ in range(target_records):
        order_id = f"ORD-{order_id_counter}"
        order_id_counter += 1
        
        # Pick date based on seasonal weights
        day_idx = np.random.choice(total_days, p=day_weights)
        order_dt = start_dt + timedelta(days=int(day_idx), hours=random.randint(8, 22), minutes=random.randint(0, 59))
        
        # Pick customer
        cust = np.random.choice(customers, p=customer_weights)
        
        # Pick product
        prod = np.random.choice(products, p=prod_weights)
        
        # Quantity based on category & price
        if prod["unit_price"] > 600:
            quantity = np.random.choice([1, 2, 3], p=[0.78, 0.18, 0.04])
        elif prod["unit_price"] > 150:
            quantity = np.random.choice([1, 2, 3, 4], p=[0.60, 0.25, 0.10, 0.05])
        else:
            quantity = np.random.choice([1, 2, 3, 4, 5, 6, 8, 10], p=[0.40, 0.25, 0.15, 0.08, 0.05, 0.03, 0.02, 0.02])
            
        # Realistic discounts (mostly 0%, with promotional 5%, 10%, 15%, 20%, 25%)
        # Corporate gets slight bulk discounts
        if cust["customer_segment"] == "Corporate":
            discount = np.random.choice([0.0, 0.05, 0.10, 0.15, 0.20], p=[0.40, 0.25, 0.20, 0.10, 0.05])
        else:
            discount = np.random.choice([0.0, 0.05, 0.10, 0.15, 0.20, 0.25], p=[0.55, 0.18, 0.14, 0.07, 0.04, 0.02])
            
        discount = min(discount, prod["discount_max"])
        
        unit_price = prod["unit_price"]
        unit_cost = prod["cost"]
        
        # Calculate financial metrics
        gross_sales = quantity * unit_price
        discount_amount = round(gross_sales * discount, 2)
        sales = round(gross_sales - discount_amount, 2)
        total_cost = round(quantity * unit_cost, 2)
        profit = round(sales - total_cost, 2)
        
        # Payment method
        if random.random() < 0.85:
            payment_method = cust["preferred_payment"]
        else:
            payment_method = random.choice(PAYMENT_METHODS)
            
        rows.append({
            "order_id": order_id,
            "order_date": order_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "customer_id": cust["customer_id"],
            "customer_name": cust["customer_name"],
            "product_id": prod["product_id"],
            "product_name": prod["product_name"],
            "category": prod["category"],
            "quantity": int(quantity),
            "unit_price": float(unit_price),
            "discount": float(discount),
            "sales": float(sales),
            "cost": float(total_cost),
            "profit": float(profit),
            "region": cust["region"],
            "city": cust["city"],
            "payment_method": payment_method,
            "customer_segment": cust["customer_segment"]
        })
        
    df = pd.DataFrame(rows)
    return df

def inject_raw_data_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Inject realistic raw data anomalies (missing values, duplicates, format inconsistencies)
    to reflect real-world transactional extracts before the cleaning pipeline.
    """
    raw_df = df.copy()
    
    # 1. Inject ~1.2% duplicate rows
    num_dupes = int(len(raw_df) * 0.012)
    dupe_rows = raw_df.sample(n=num_dupes, random_state=RANDOM_SEED)
    raw_df = pd.concat([raw_df, dupe_rows], ignore_index=True)
    
    # 2. Inject ~0.8% missing customer names (blank/null)
    null_cust_indices = raw_df.sample(frac=0.008, random_state=RANDOM_SEED).index
    raw_df.loc[null_cust_indices, "customer_name"] = np.nan
    
    # 3. Inject ~0.5% missing payment methods
    null_pay_indices = raw_df.sample(frac=0.005, random_state=RANDOM_SEED+1).index
    raw_df.loc[null_pay_indices, "payment_method"] = None
    
    # 4. Inject slight whitespace discrepancies in category & region
    whitespace_indices = raw_df.sample(frac=0.02, random_state=RANDOM_SEED+2).index
    raw_df.loc[whitespace_indices, "category"] = raw_df.loc[whitespace_indices, "category"].apply(lambda x: f"  {x}  ")
    
    # 5. Inject a few mixed date formats (e.g. DD/MM/YYYY or YYYY/MM/DD)
    date_noise_indices = raw_df.sample(frac=0.015, random_state=RANDOM_SEED+3).index
    for idx in date_noise_indices:
        orig_val = raw_df.loc[idx, "order_date"]
        try:
            dt = datetime.strptime(orig_val, "%Y-%m-%d %H:%M:%S")
            raw_df.loc[idx, "order_date"] = dt.strftime("%d/%m/%Y")
        except Exception:
            pass

    # Shuffle the dataset
    raw_df = raw_df.sample(frac=1.0, random_state=RANDOM_SEED).reset_index(drop=True)
    return raw_df

def load_or_create_raw_data(
    raw_path: str = "data/raw/raw_ecommerce_data.csv",
    force_recreate: bool = False
) -> pd.DataFrame:
    """Load raw dataset if exists, or generate and persist it."""
    if os.path.exists(raw_path) and not force_recreate:
        print(f"Loading existing raw data from: {raw_path}")
        return pd.read_csv(raw_path)
    
    print("Generating enterprise-grade synthetic e-commerce raw data...")
    clean_base_df = generate_synthetic_dataset(target_records=12500)
    raw_df = inject_raw_data_anomalies(clean_base_df)
    
    os.makedirs(os.path.dirname(raw_path), exist_ok=True)
    raw_df.to_csv(raw_path, index=False)
    print(f"Saved raw dataset to: {raw_path} ({len(raw_df):,} records)")
    return raw_df

if __name__ == "__main__":
    df = load_or_create_raw_data(force_recreate=True)
    print("\nDataset Summary:")
    print(f"- Total Records: {len(df):,}")
    print(f"- Unique Customers: {df['customer_id'].nunique():,}")
    print(f"- Unique Products: {df['product_id'].nunique():,}")
    print(f"- Date Range: {df['order_date'].min()} to {df['order_date'].max()}")
    print("\nSample Rows:")
    print(df.head(3))
