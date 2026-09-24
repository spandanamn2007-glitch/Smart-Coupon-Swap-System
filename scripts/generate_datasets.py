"""
Phase 3 Dataset Generation Script
Smart Coupon Swap System

Generates synthetic datasets for data science and ML experimentation.
All data is fictional. No real personal information is used.

SEED = 42 -- all outputs are fully reproducible.

Run:
    python scripts/generate_datasets.py

Output directory: data/raw/
"""

import os
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

CITIES_STATES = [
    ("Mumbai","Maharashtra"), ("Delhi","Delhi"), ("Bengaluru","Karnataka"),
    ("Hyderabad","Telangana"), ("Ahmedabad","Gujarat"), ("Chennai","Tamil Nadu"),
    ("Kolkata","West Bengal"), ("Pune","Maharashtra"), ("Jaipur","Rajasthan"),
    ("Lucknow","Uttar Pradesh"), ("Surat","Gujarat"), ("Kochi","Kerala"),
    ("Chandigarh","Punjab"), ("Bhopal","Madhya Pradesh"), ("Indore","Madhya Pradesh"),
    ("Nagpur","Maharashtra"), ("Visakhapatnam","Andhra Pradesh"),
    ("Coimbatore","Tamil Nadu"), ("Patna","Bihar"), ("Vadodara","Gujarat"),
]
CITY_NAMES = [c for c, _ in CITIES_STATES]

REVIEW_TEXTS = [
    "Great swap, very smooth!", "Coupon was valid and worked perfectly.",
    "Fast response and easy process.", "Happy with the exchange.",
    "Would swap again.", "Smooth experience overall.",
    "Coupon was exactly as described.", "Trustworthy user.",
    "Minor delay but resolved quickly.", "Good deal, satisfied.",
    "No issues at all.", "Quick and easy swap.",
    "Coupon worked as expected.", "Very responsive user.",
    "Would recommend to others.", "Seamless transaction.",
    "Fair exchange.", "Had a great experience.",
    "Very professional.", "Will use this platform again.",
]


def rand_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))

def rand_datetime(start, end):
    delta = int((end - start).total_seconds())
    return start + timedelta(seconds=random.randint(0, max(delta, 1)))

def save(df, filename):
    df.to_csv(os.path.join(OUTPUT_DIR, filename), index=False)
    print(f"  [OK] {filename:<36} {len(df):>6} records")


# 1. Categories
def generate_categories():
    data = [
        ("CAT01","Food"), ("CAT02","Fashion"), ("CAT03","Electronics"),
        ("CAT04","Travel"), ("CAT05","Grocery"), ("CAT06","Beauty"),
        ("CAT07","Entertainment"), ("CAT08","Sports"),
        ("CAT09","Health"), ("CAT10","Home"),
    ]
    df = pd.DataFrame(data, columns=["category_id","category_name"])
    save(df, "categories.csv")
    return df


# 2. Brands
def generate_brands(categories_df):
    brand_data = [
        ("B001","QuickBite","CAT01"), ("B002","TastyTreats","CAT01"),
        ("B003","SpiceRoute","CAT01"), ("B004","FreshBowl","CAT01"),
        ("B005","TrendWear","CAT02"), ("B006","StyleHub","CAT02"),
        ("B007","UrbanThreads","CAT02"), ("B008","DenimCo","CAT02"),
        ("B009","TechNova","CAT03"), ("B010","GadgetZone","CAT03"),
        ("B011","CircuitPlus","CAT03"), ("B012","DigiMart","CAT03"),
        ("B013","WanderFly","CAT04"), ("B014","RoamEasy","CAT04"),
        ("B015","TripNest","CAT04"), ("B016","JetSetGo","CAT04"),
        ("B017","FreshCart","CAT05"), ("B018","DailyBasket","CAT05"),
        ("B019","GreenMart","CAT05"), ("B020","PantryDirect","CAT05"),
        ("B021","GlowCo","CAT06"), ("B022","PureSkin","CAT06"),
        ("B023","BeautyBliss","CAT06"),
        ("B024","StreamFlix","CAT07"), ("B025","GameVault","CAT07"),
        ("B026","CinemaHub","CAT07"),
        ("B027","FitGear","CAT08"), ("B028","SportZone","CAT08"),
        ("B029","AthletePro","CAT08"),
        ("B030","WellnessRx","CAT09"), ("B031","MediCare","CAT09"),
        ("B032","HealthPlus","CAT09"),
        ("B033","HomeNest","CAT10"), ("B034","DecorMart","CAT10"),
        ("B035","FurniWave","CAT10"), ("B036","LivingSpace","CAT10"),
    ]
    df = pd.DataFrame(brand_data, columns=["brand_id","brand_name","category_id"])
    save(df, "brands.csv")
    return df


# 3. Users
def generate_users(n=500):
    genders = ["Male","Female","Other"]
    gender_w = [0.48, 0.48, 0.04]
    activities = ["low","medium","high"]
    act_w = [0.25, 0.50, 0.25]
    start = datetime(2022, 1, 1)
    end   = datetime(2024, 12, 31)
    rows = []
    for i in range(1, n+1):
        pmin = random.randint(5, 40)
        pmax = pmin + random.randint(10, 50)
        city, state = random.choice(CITIES_STATES)
        rows.append({
            "user_id": f"U{i:04d}",
            "age": random.randint(18, 65),
            "gender": random.choices(genders, weights=gender_w)[0],
            "city": city, "state": state,
            "account_created_date": rand_date(start, end).strftime("%Y-%m-%d"),
            "preferred_discount_min": pmin,
            "preferred_discount_max": pmax,
            "activity_level": random.choices(activities, weights=act_w)[0],
        })
    df = pd.DataFrame(rows)
    save(df, "users.csv")
    return df


# 4. Coupons
def generate_coupons(users_df, categories_df, brands_df, n=2500):
    user_ids = users_df["user_id"].tolist()
    cat_ids  = categories_df["category_id"].tolist()
    cat_brands = {}
    for _, r in brands_df.iterrows():
        cat_brands.setdefault(r["category_id"], []).append(r["brand_id"])
    d_types   = ["percentage","flat"]
    d_type_w  = [0.65, 0.35]
    statuses  = ["available","claimed","expired","swapped"]
    status_w  = [0.45, 0.20, 0.20, 0.15]
    sources   = ["purchased","gifted","earned","referral"]
    source_w  = [0.30, 0.25, 0.30, 0.15]
    flat_vals = [50,75,100,150,200,250,300,400,500]
    start = datetime(2023,1,1)
    end   = datetime(2024,12,31)
    rows = []
    for i in range(1, n+1):
        cat_id  = random.choice(cat_ids)
        brand_id = random.choice(cat_brands[cat_id])
        d_type  = random.choices(d_types, weights=d_type_w)[0]
        d_value = round(random.uniform(5.0,80.0),1) if d_type=="percentage" else float(random.choice(flat_vals))
        issue   = rand_date(start, end)
        expiry  = issue + timedelta(days=random.randint(30, 365))
        rows.append({
            "coupon_id":       f"CP{i:04d}",
            "owner_id":        random.choice(user_ids),
            "category_id":     cat_id,
            "brand_id":        brand_id,
            "discount_type":   d_type,
            "discount_value":  d_value,
            "minimum_purchase": random.choice([0,199,299,499,999,1499,1999]),
            "issue_date":      issue.strftime("%Y-%m-%d"),
            "expiry_date":     expiry.strftime("%Y-%m-%d"),
            "coupon_value":    round(random.uniform(50.0, 5000.0), 2),
            "status":          random.choices(statuses, weights=status_w)[0],
            "city":            random.choice(CITY_NAMES),
            "source":          random.choices(sources, weights=source_w)[0],
            "transferable":    random.choice(["yes","no"]),
        })
    df = pd.DataFrame(rows)
    save(df, "coupons.csv")
    return df


# 5. User Preferences
def generate_user_preferences(users_df, categories_df, brands_df):
    user_ids = users_df["user_id"].tolist()
    cat_ids  = categories_df["category_id"].tolist()
    cat_brands = {}
    for _, r in brands_df.iterrows():
        cat_brands.setdefault(r["category_id"], []).append(r["brand_id"])
    d_types = ["percentage","flat","any"]
    rows = []
    pid = 1
    for uid in user_ids:
        for _ in range(random.randint(1,4)):
            cat_id = random.choice(cat_ids)
            rows.append({
                "preference_id":           f"PR{pid:04d}",
                "user_id":                 uid,
                "preferred_category_id":   cat_id,
                "preferred_brand_id":      random.choice(cat_brands[cat_id]),
                "minimum_discount":        random.randint(5,50),
                "preferred_city":          random.choice(CITY_NAMES),
                "preferred_discount_type": random.choice(d_types),
            })
            pid += 1
    df = pd.DataFrame(rows)
    save(df, "user_preferences.csv")
    return df


# 6. Coupon Views
def generate_coupon_views(users_df, coupons_df, n=5000):
    user_ids   = users_df["user_id"].tolist()
    coupon_ids = coupons_df["coupon_id"].tolist()
    start = datetime(2023,1,1)
    end   = datetime(2025,3,31)
    rows = [{"view_id":f"V{i:05d}","user_id":random.choice(user_ids),
             "coupon_id":random.choice(coupon_ids),
             "viewed_at":rand_datetime(start,end).strftime("%Y-%m-%d %H:%M:%S"),
             "view_duration_seconds":random.randint(5,300)} for i in range(1,n+1)]
    df = pd.DataFrame(rows)
    save(df, "coupon_views.csv")
    return df


# 7. Coupon Requests
def generate_coupon_requests(users_df, coupons_df, n=1500):
    user_ids   = users_df["user_id"].tolist()
    coupon_ids = coupons_df["coupon_id"].tolist()
    statuses = ["pending","accepted","rejected","cancelled"]
    stat_w   = [0.30, 0.30, 0.25, 0.15]
    start = datetime(2023,1,1)
    end   = datetime(2025,3,31)
    rows = [{"request_id":f"REQ{i:04d}","user_id":random.choice(user_ids),
             "coupon_id":random.choice(coupon_ids),
             "requested_at":rand_datetime(start,end).strftime("%Y-%m-%d %H:%M:%S"),
             "request_status":random.choices(statuses, weights=stat_w)[0]} for i in range(1,n+1)]
    df = pd.DataFrame(rows)
    save(df, "coupon_requests.csv")
    return df


# 8. Coupon Usage
def generate_coupon_usage(users_df, coupons_df, n=1000):
    user_ids   = users_df["user_id"].tolist()
    coupon_ids = coupons_df["coupon_id"].tolist()
    statuses = ["used","expired","cancelled"]
    stat_w   = [0.60, 0.25, 0.15]
    start = datetime(2023,1,1)
    end   = datetime(2025,3,31)
    rows = [{"usage_id":f"USE{i:04d}","user_id":random.choice(user_ids),
             "coupon_id":random.choice(coupon_ids),
             "used_at":rand_datetime(start,end).strftime("%Y-%m-%d %H:%M:%S"),
             "usage_status":random.choices(statuses, weights=stat_w)[0]} for i in range(1,n+1)]
    df = pd.DataFrame(rows)
    save(df, "coupon_usage.csv")
    return df


# 9. Swaps
def generate_swaps(users_df, coupons_df, n=500):
    user_ids   = users_df["user_id"].tolist()
    coupon_ids = coupons_df["coupon_id"].tolist()
    statuses = ["proposed","accepted","rejected","completed","cancelled"]
    stat_w   = [0.15, 0.15, 0.20, 0.35, 0.15]
    start = datetime(2023,1,1)
    end   = datetime(2025,3,31)
    rows = []
    meta = []
    for i in range(1, n+1):
        proposer = random.choice(user_ids)
        receiver = random.choice([u for u in user_ids if u != proposer])
        offered  = random.choice(coupon_ids)
        requested = random.choice([c for c in coupon_ids if c != offered])
        status = random.choices(statuses, weights=stat_w)[0]
        prop_dt = rand_datetime(start, end)
        comp_at = ""
        if status in ("accepted","completed"):
            comp_at = (prop_dt + timedelta(hours=random.randint(1,72))).strftime("%Y-%m-%d %H:%M:%S")
        sid = f"SW{i:04d}"
        rows.append({"swap_id":sid,"proposer_id":proposer,"receiver_id":receiver,
                     "offered_coupon_id":offered,"requested_coupon_id":requested,
                     "proposed_at":prop_dt.strftime("%Y-%m-%d %H:%M:%S"),
                     "completed_at":comp_at,"swap_status":status})
        meta.append((sid, proposer, receiver, status, prop_dt))
    df = pd.DataFrame(rows)
    save(df, "swaps.csv")
    return df, meta


# 10. Ratings
def generate_ratings(swap_meta):
    rateable = [(sid,prop,recv,pdt) for sid,prop,recv,st,pdt in swap_meta
                if st in ("accepted","completed")]
    rows = []
    rid = 1
    for sid, proposer, receiver, prop_dt in rateable:
        if random.random() < 0.85:
            rows.append({"rating_id":f"RAT{rid:04d}","swap_id":sid,
                         "rater_id":proposer,"rated_user_id":receiver,
                         "rating":random.randint(1,5),"review_text":random.choice(REVIEW_TEXTS),
                         "rated_at":(prop_dt+timedelta(hours=random.randint(24,168))).strftime("%Y-%m-%d %H:%M:%S")})
            rid += 1
        if random.random() < 0.75:
            rows.append({"rating_id":f"RAT{rid:04d}","swap_id":sid,
                         "rater_id":receiver,"rated_user_id":proposer,
                         "rating":random.randint(1,5),"review_text":random.choice(REVIEW_TEXTS),
                         "rated_at":(prop_dt+timedelta(hours=random.randint(24,168))).strftime("%Y-%m-%d %H:%M:%S")})
            rid += 1
    df = pd.DataFrame(rows)
    save(df, "ratings.csv")
    return df


def main():
    print("=" * 60)
    print("PHASE 3 - DATASET GENERATION")
    print("Smart Coupon Swap System | Seed:", SEED)
    print("=" * 60)
    cats   = generate_categories()
    brands = generate_brands(cats)
    users  = generate_users(500)
    coupons = generate_coupons(users, cats, brands, 2500)
    generate_user_preferences(users, cats, brands)
    generate_coupon_views(users, coupons, 5000)
    generate_coupon_requests(users, coupons, 1500)
    generate_coupon_usage(users, coupons, 1000)
    _, meta = generate_swaps(users, coupons, 500)
    generate_ratings(meta)
    print("=" * 60)
    print("All datasets generated successfully.")
    print("=" * 60)

if __name__ == "__main__":
    main()
