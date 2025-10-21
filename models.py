from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from slugify import slugify
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import time

db = SQLAlchemy()

# ============================================================
# MODELO DE USUARIO
# ============================================================
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # -------------------------------
    # Métodos de utilidad
    # -------------------------------
    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def save(self):
        db.session.add(self)
        try:
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

    @staticmethod
    def get_by_id(user_id):
        return User.query.get(user_id)

    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()

    def __repr__(self):
        return f"<User {self.email}>"

# ============================================================
# MODELO DE PRODUCTO
# ============================================================
class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price_cents = db.Column(db.Numeric(12, 2), nullable=False)
    size = db.Column(db.String(50), nullable=True)
    image_filename = db.Column(db.String(255), nullable=True)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    owner = db.relationship("User", backref=db.backref("products", lazy=True))

    # -------------------------------
    # Métodos de utilidad
    # -------------------------------
    def _generate_unique_slug(self):
        base = slugify(self.title)
        if not base:
            base = f"product-{int(time.time())}"
        candidate = base
        counter = 1
        while Product.query.filter_by(slug=candidate).first():
            counter += 1
            candidate = f"{base}-{counter}"
        return candidate

    def save(self):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        db.session.add(self)
        try:
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            self.slug = self._generate_unique_slug()
            db.session.add(self)
            try:
                db.session.commit()
                return True
            except IntegrityError:
                db.session.rollback()
                return False

    def public_url(self):
        return f"/product/{self.slug}/"

    @staticmethod
    def get_by_slug(slug):
        return Product.query.filter_by(slug=slug).first()

    @staticmethod
    def get_all():
        return Product.query.order_by(Product.created_at.desc()).all()

    def __repr__(self):
        return f"<Product {self.title} ({self.slug})>"

# ============================================================
# MODELO DE ITEM EN CARRITO
# ============================================================
class CartItem(db.Model):
    __tablename__ = "cart_items"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    session_id = db.Column(db.String(100), nullable=True)
    qty = db.Column(db.Integer, default=1)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship("Product", backref=db.backref("cart_items", lazy=True))

    def subtotal(self):
        return float(self.qty) * float(self.product.price)

    def __repr__(self):
        return f"<CartItem product_id={self.product_id} qty={self.qty}>"
