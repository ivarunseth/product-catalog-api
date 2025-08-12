from flask import request, jsonify, current_app
from ..models import db, Product, ProductImage, Category
from . import api

@api.route('/products', methods=['POST'])
def create_product():
    data = request.json

    # Validate required fields
    title = data.get('title')
    if not title:
        return jsonify({'error': 'title required'}), 400

    price = float(data.get('price', 0.0))
    p = Product(
        title=title,
        description=data.get('description', ''),
        price_cents=int(price * 100),
        currency=data.get('currency', 'INR')
    )

    # Assign brand if provided
    brand_id = data.get('brand_id')
    if brand_id:
        p.brand_id = brand_id

    p.set_slug()

    # Handle images — now expects Base64 strings
    # Format: [{ "data": "<base64string>", "mime_type": "image/png" }, ...]
    images = data.get('images', [])
    for i, img in enumerate(images):
        if isinstance(img, dict):
            base64_data = img.get('data')
            mime_type = img.get('mime_type', 'image/jpeg')
        else:
            # Fallback: assume plain Base64 string and default to JPEG
            base64_data = img
            mime_type = 'image/jpeg'

        if base64_data:
            pi = ProductImage(data=base64_data, mime_type=mime_type, position=i)
            p.images.append(pi)

    # Handle categories
    cat_ids = data.get('category_ids', [])
    for cid in cat_ids:
        cat = Category.query.get(cid)
        if cat:
            p.categories.append(cat)

    # Save to DB
    db.session.add(p)
    db.session.commit()

    # Invalidate cache if used
    if hasattr(current_app, "cache"):
        current_app.cache.delete('product:*')
        current_app.cache.delete('filters:*')

    return jsonify(p.to_dict()), 201
