import os
import re
import csv
import base64
import random
import requests
from lorem_text import lorem
from flask import Flask
from tqdm import tqdm

from . import create_app, db
from .models import Product, Category, ProductImage, Brand

DATA_DIR = "./data"  # path to your CSV files
PRODUCTS_PER_MAIN_CATEGORY = 100


def download_image_as_base64(url):
    try:
        payload = {}
        headers = {}

        resp = requests.request("GET", url, headers=headers, data=payload)
        resp.raise_for_status()
        return base64.b64encode(resp.content).decode("utf-8"), resp.headers.get("Content-Type", "image/jpeg")
    except Exception as e:
        print(f"Failed to download {url}: {e}")
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


def seed():
    brand = Brand.query.filter_by(name="Generic Brand").first()
    if not brand:
        brand = Brand(name="Generic Brand")
        db.session.add(brand)
        db.session.commit()

    csv_files = [os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR) if f.endswith(".csv")]

    for file_path in csv_files:
        with open(file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            main_category_counts = {}

            for row in tqdm(reader, desc=f"Seeding {os.path.basename(file_path)}"):
                main_cat_name = row["main_category"].strip()
                sub_cat_name = row["sub_category"].strip() if row.get("sub_category") else None

                count = main_category_counts.get(main_cat_name, 0)
                if count >= PRODUCTS_PER_MAIN_CATEGORY:
                    continue

                category = get_or_create_category(main_cat_name, sub_cat_name)

                price_str = re.sub(r"[^\d.]", "", row["actual_price"])
                if not price_str:
                    continue
                price = float(price_str)

                image_base64, mime_type = download_image_as_base64(row["image"])
                if not image_base64:
                    continue

                product = Product(
                    title=row["name"].strip(),
                    description=f"{row['name'].strip()}. {lorem.paragraph()}",
                    price_cents=int(price * 100),
                    currency="USD",
                    brand=brand
                )
                product.set_slug()
                product.categories.append(category)

                img = ProductImage(
                    data=image_base64,
                    mime_type=mime_type or "image/jpeg",
                    position=0
                )
                product.images.append(img)

                db.session.add(product)
                main_category_counts[main_cat_name] = count + 1

            db.session.commit()


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed()
        print("✅ Seeding complete!")
