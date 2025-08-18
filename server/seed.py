import os
import re
import csv
import base64
import requests
import kagglehub
from lorem_text import lorem
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

from . import create_app, db
from .models import Product, Category, ProductImage, Brand


PRODUCTS_PER_MAIN_CATEGORY = 100
MAX_WORKERS = 16  # tune based on bandwidth/remote rate limits/DB pool


def download_image_as_base64(url):
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/115.0 Safari/537.36"
            ),
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.amazon.com/",
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        return base64.b64encode(resp.content).decode("utf-8"), resp.headers.get("Content-Type", "image/jpeg")
    except Exception as e:
        return None, None

def get_or_create_category(main_cat_name, sub_cat_name):
    main_cat = Category.query.filter_by(name=main_cat_name, parent_id=None).first()
    if not main_cat:
        main_cat = Category(name=main_cat_name)
        db.session.add(main_cat)
        db.session.commit()

    sub_cat = None
    if sub_cat_name:
        sub_cat = Category.query.filter_by(name=sub_cat_name, parent_id=main_cat.id).first()
        if not sub_cat:
            sub_cat = Category(name=sub_cat_name, parent=main_cat)
            db.session.add(sub_cat)
            db.session.commit()

    return sub_cat or main_cat

def get_or_create_brand_from_name(product_name):
    brand_name = product_name.split()[0].strip() or "Unknown"
    brand = Brand.query.filter_by(name=brand_name).first()
    if not brand:
        brand = Brand(name=brand_name)
        db.session.add(brand)
        db.session.commit()
    return brand

def parse_price(price_str):
    price_clean = re.sub(r"[^\d.]", "", price_str or "")
    if not price_clean:
        return None
    try:
        return float(price_clean)
    except ValueError:
        return None

def seed():
    # Download latest version
    path = kagglehub.dataset_download("lokeshparab/amazon-products-dataset")
    print("Path to dataset files:", path)

    csv_files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(".csv")]

    for file_path in csv_files:
        # 1) Load rows first
        rows = []
        with open(file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                rows.append(row)

        # 2) Filter/prepare jobs respecting per-main-category cap
        main_category_counts = {}
        jobs = []
        for row in rows:
            main_cat_name = (row.get("main_category") or "").strip()
            if not main_cat_name:
                continue
            count = main_category_counts.get(main_cat_name, 0)
            if count >= PRODUCTS_PER_MAIN_CATEGORY:
                continue

            # quick price validation before downloading
            price = parse_price(row.get("actual_price"))
            if price is None:
                continue

            img_url = row.get("image")
            if not img_url:
                continue

            # Reserve a slot for this main category; will rollback on failure
            main_category_counts[main_cat_name] = count + 1
            jobs.append({
                "main_category": main_cat_name,
                "sub_category": (row.get("sub_category") or "").strip() or None,
                "name": (row.get("name") or "").strip(),
                "price": price,
                "image": img_url,
            })

        # 3) Parallelize image downloads only
        results = []
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_job = {executor.submit(download_image_as_base64, job["image"]): job for job in jobs}
            for future in tqdm(as_completed(future_to_job), total=len(future_to_job), desc=f"Downloading images for {os.path.basename(file_path)}"):
                job = future_to_job[future]
                try:
                    image_base64, mime_type = future.result()
                except Exception:
                    image_base64, mime_type = None, None

                # If download failed, release the reserved count
                if not image_base64:
                    main_category_counts[job["main_category"]] -= 1
                    continue

                results.append((job, image_base64, mime_type or "image/jpeg"))

        # 4) Persist to DB in the main thread/session
        for job, image_base64, mime_type in tqdm(results, desc=f"Seeding DB for {os.path.basename(file_path)}"):
            # Resolve category and brand with session-safe calls
            category = get_or_create_category(job["main_category"], job["sub_category"])
            brand = get_or_create_brand_from_name(job["name"])

            product = Product(
                title=job["name"],
                description=f"{job['name']}. {lorem.paragraph()}",
                price=int(job["price"] * 100),
                currency="INR",
                brand=brand
            )
            product.set_slug()
            product.categories.append(category)

            img = ProductImage(
                data=image_base64,
                mime_type=mime_type,
                position=0
            )
            product.images.append(img)

            db.session.add(product)

        db.session.commit()

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed()
        print("✅ Seeding complete!")
