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

    payload = product.to_dict()
    payload['breadcrumb'] = breadcrumb

    current_app.cache.set(cache_key, payload, ttl=30 * 60)
    return jsonify(payload)


@api.route('/products/search', methods=['GET'])
def product_search():
    q = request.args.get('q', '') or ''
    category_id = request.args.get('category_id')
    brand_id = request.args.get('brand_id')
    sort_price = request.args.get('sort_price', None)

    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    try:
        limit = int(request.args.get('limit', 12))
    except ValueError:
        limit = 12

    cache_key = f"search:q={q}:cat={category_id}:brand={brand_id}:page={page}:limit={limit}:sort_price={sort_price}"

    cached_response = current_app.cache.get(cache_key)
    if cached_response:
        return jsonify(cached_response)

    query = Product.query
    if q:
        query = query.filter(Product.title.ilike(f"%{q}%"))
    if brand_id:
        query = query.filter_by(brand_id=brand_id)
    if category_id:
        query = query.join(Product.categories).filter(Category.id == int(category_id))

    total = query.count()
    items = query

    if sort_price:
        if sort_price == 'asc':
            items = items.order_by(Product.price_cents.asc())
        elif sort_price == 'desc':
            items = items.order_by(Product.price_cents.desc())

    items = items.offset((page - 1) * limit).limit(limit)

    data = [p.to_dict(include_images=True) for p in items.all()]

    category_ids = set()
    brand_ids = set()

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

    filters = {'categories': categories, 'brands': brands}

    response_payload = {
        'total': total,
        'page': page,
        'limit': limit,
        'items': data,
        'filters': filters
    }

    if total > 0 and data:
        current_app.cache.set(cache_key, response_payload, ttl=current_app.config['CACHE_TTL'])

    return jsonify(response_payload)
