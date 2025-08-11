from flask import request, jsonify, current_app
from ..models import Product, Category, Brand
from . import api

@api.route('/products/<slug>', methods=['GET'])
def product_detail(slug):
    cache_key = f"product:slug:{slug}"
    cached = current_app.cache.get(cache_key)
    if cached:
        return jsonify(cached)

    product = Product.query.filter_by(slug=slug).first_or_404()
    breadcrumb = []
    if product.categories:
        breadcrumb = product.categories[0].breadcrumb()

    payload = product.to_dict()  # Already returns Base64 images
    payload['breadcrumb'] = breadcrumb

    current_app.cache.set(cache_key, payload, ttl=30 * 60)
    return jsonify(payload)


@api.route('/products/search', methods=['GET'])
def product_search():
    q = request.args.get('q', '') or ''
    category_id = request.args.get('category_id')
    brand_id = request.args.get('brand_id')

    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    try:
        limit = int(request.args.get('limit', 12))
    except ValueError:
        limit = 12

    query = Product.query
    if q:
        query = query.filter(Product.title.ilike(f"%{q}%"))
    if brand_id:
        query = query.filter_by(brand_id=brand_id)
    if category_id:
        query = query.join(Product.categories).filter(Category.id == int(category_id))

    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()

    # Images are already returned as base64 data URIs
    data = [p.to_dict(include_images=True) for p in items]

    filters_key = f"filters:q={q}:cat={category_id}:brand={brand_id}"
    cached_filters = current_app.cache.get(filters_key)

    if not cached_filters:
        category_ids = set()
        brand_ids = set()

        # Limit filter computation to first 500 products
        for p in query.limit(500).all():
            if p.brand_id:
                brand_ids.add(p.brand_id)
            for c in p.categories:
                category_ids.add(c.id)

        categories = [
            {'id': c.id, 'name': c.name}
            for c in Category.query.filter(Category.id.in_(list(category_ids))).all()
        ] if category_ids else []

        brands = [
            {'id': b.id, 'name': b.name}
            for b in Brand.query.filter(Brand.id.in_(list(brand_ids))).all()
        ] if brand_ids else []

        cached_filters = {'categories': categories, 'brands': brands}
        current_app.cache.set(filters_key, cached_filters, ttl=60 * 60)

    return jsonify({
        'total': total,
        'page': page,
        'limit': limit,
        'items': data,
        'filters': cached_filters
    })
