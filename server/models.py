from datetime import datetime
from slugify import slugify
from . import db

product_category = db.Table(
    'product_category',
    db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id'), primary_key=True)
)

class Brand(db.Model):
    __tablename__ = 'brands'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    parent = db.relationship('Category', remote_side=[id], backref='children')

    def breadcrumb(self):
        node = self
        path = []
        while node:
            path.append({'id': node.id, 'name': node.name})
            node = node.parent
        return list(reversed(path))


class ProductImage(db.Model):
    __tablename__ = "product_images"

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Text, nullable=False)  # Base64-encoded image data
    mime_type = db.Column(db.String(50), default="image/jpeg")  # For correct browser display
    position = db.Column(db.Integer, default=0)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)

    product = db.relationship("Product", back_populates="images")


class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Integer, nullable=False, default=0)
    currency = db.Column(db.String(8), default='INR')
    slug = db.Column(db.String(300), unique=True, index=True)
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    brand = db.relationship('Brand')
    
    categories = db.relationship(
        'Category', 
        secondary=product_category, 
        backref='products'
    )

    images = db.relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="ProductImage.position"
    )

    def set_slug(self):
        base = slugify(self.title)[:200]
        slug = base
        i = 1
        while Product.query.filter_by(slug=slug).first():
            slug = f"{base}-{i}"
            i += 1
        self.slug = slug

    def to_dict(self, include_images=True, include_brand=True, include_categories=True):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'price': (self.price or 0) / 100.0,
            'currency': self.currency,
            'slug': self.slug,
            'brand': {'id': self.brand.id, 'name': self.brand.name} if (self.brand and include_brand) else None,
            'images': [
                {
                    'src': f"data:{img.mime_type};base64,{img.data}",
                    'position': img.position
                }
                for img in self.images
            ] if include_images else [],
            'categories': [{'id': c.id, 'name': c.name} for c in self.categories] if include_categories else []
        }
