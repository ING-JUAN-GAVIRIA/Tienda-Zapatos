import os
from flask import Flask, render_template, redirect, url_for, flash, request, abort, session
from config import Config
from models import db, User, Product, CartItem
from forms import SignupForm, LoginForm, ProductForm, EditProductForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from urllib.parse import urlparse, urljoin
from werkzeug.utils import secure_filename


def is_safe_url(target):
    host_url = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))
    return (redirect_url.scheme in ("http", "https")) and (host_url.netloc == redirect_url.netloc)


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)
    app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # 4MB

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(int(user_id))

    @app.before_request
    def create_tables_once():
        """Crea las tablas solo la primera vez que se ejecuta la app."""
        if not hasattr(app, '_tables_created'):
            with app.app_context():
                db.create_all()
            app._tables_created = True

    # ------------------ RUTAS PRINCIPALES ------------------

    @app.route("/")
    def index():
        products = Product.get_all()
        return render_template("index.html", products=products)

    @app.route("/product/<slug>/")
    def product_view(slug):
        product = Product.get_by_slug(slug)
        if not product:
            abort(404)
        return render_template("product_view.html", product=product)

    # ------------------ USUARIOS ------------------

    @app.route("/signup/", methods=["GET", "POST"])
    def signup():
        if current_user.is_authenticated:
            return redirect(url_for("index"))
        form = SignupForm()
        if form.validate_on_submit():
            u = User(username=form.username.data, email=form.email.data)
            u.set_password(form.password.data)
            ok = u.save()
            if not ok:
                flash("Error al crear usuario. El email puede estar en uso.", "danger")
                return render_template("signup_form.html", form=form)
            login_user(u)

            _merge_cart_with_session(u)

            flash("Cuenta creada y sesión iniciada.", "success")
            next_page = request.args.get("next")
            if next_page and is_safe_url(next_page):
                return redirect(next_page)
            return redirect(url_for("index"))
        return render_template("signup_form.html", form=form)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("index"))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.get_by_email(form.email.data)
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)

                _merge_cart_with_session(user)

                flash("Inicio de sesión correcto.", "success")
                next_page = request.args.get("next")
                if next_page and is_safe_url(next_page):
                    return redirect(next_page)
                return redirect(url_for("index"))
            flash("Credenciales inválidas.", "danger")
        return render_template("login_form.html", form=form)

    @app.route("/logout")
    def logout():
        if current_user.is_authenticated:
            logout_user()
            flash("Cerraste sesión.", "info")
        return redirect(url_for("index"))

    # ------------------ PRODUCTOS ------------------

    @app.route("/product/add", methods=["GET", "POST"])
    @login_required
    def create_product():
        form = ProductForm()
        if form.validate_on_submit():
            filename = None
            if form.image.data:
                filename = secure_filename(form.image.data.filename)
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                form.image.data.save(filepath)

            p = Product(
                user_id=current_user.id,
                title=form.title.data.strip(),
                description=form.description.data.strip(),
                price=form.price.data,
                size=form.size.data.strip() if form.size.data else None,
                image_filename=filename,
                slug=None
            )

            if p.save():
                flash("Producto creado correctamente", "success")
                return redirect(url_for('product_view', slug=p.slug))
            flash("Error guardando producto", "danger")
        return render_template('admin/product_form.html', form=form)

    @app.route('/product/edit/<int:product_id>', methods=['GET', 'POST'])
    @login_required
    def edit_product(product_id):
        product = Product.query.get_or_404(product_id)
        if product.user_id != current_user.id and not current_user.is_admin:
            flash('No tienes permisos para editar.', 'danger')
            return redirect(url_for('index'))
        form = EditProductForm(obj=product)
        if form.validate_on_submit():
            if form.image.data:
                filename = secure_filename(form.image.data.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                form.image.data.save(filepath)
                product.image_filename = filename
            product.title = form.title.data.strip()
            product.description = form.description.data.strip()
            product.price_cents = int(form.price_cents.data * 100)
            product.size = form.size.data.strip() if form.size.data else None
            if product.save():
                flash('Producto actualizado.', 'success')
                return redirect(url_for('product_view', slug=product.slug))
            flash('Error al actualizar.', 'danger')
        return render_template('admin/product_edit.html', form=form, product=product)

    @app.route('/product/delete/<int:product_id>', methods=['POST'])
    @login_required
    def delete_product(product_id):
        product = Product.query.get_or_404(product_id)
        if product.user_id != current_user.id and not current_user.is_admin:
            flash('No tienes permisos para eliminar.', 'danger')
            return redirect(url_for('index'))
        try:
            db.session.delete(product)
            db.session.commit()
            flash('Producto eliminado.', 'info')
        except Exception:
            db.session.rollback()
            flash('Error al eliminar.', 'danger')
        return redirect(url_for('index'))

    # ------------------ CARRITO ------------------

    def _get_cart():
        """Obtiene el carrito desde la sesión."""
        return session.get('cart', {})

    def _save_cart(cart):
        """Guarda el carrito en la sesión."""
        session['cart'] = cart
        session.modified = True

    def _merge_cart_with_session(user):
        """Fusiona el carrito en sesión con el carrito del usuario logueado."""
        session_cart = session.pop("cart", {})
        if not session_cart:
            return
        for pid, qty in session_cart.items():
            existing_item = CartItem.query.filter_by(user_id=user.id, product_id=int(pid)).first()
            if existing_item:
                existing_item.qty += qty
            else:
                db.session.add(CartItem(user_id=user.id, product_id=pid, qty=qty))
        db.session.commit()
        session.modified = True

    @app.route('/cart')
    def view_cart():
        items = []
        total_cents = 0

        if current_user.is_authenticated:
            db_items = CartItem.query.filter_by(user_id=current_user.id).all()
            for it in db_items:
                items.append({
                    'product': it.product,
                    'qty': it.qty,
                    'subtotal_cents': it.qty * it.product.price_cents
                })
                total_cents += it.qty * it.product.price_cents
        else:
            cart = session.get('cart', {})
            for pid, qty in cart.items():
                product = Product.query.get(int(pid))
                if product:
                    subtotal = qty * product.price_cents
                    items.append({
                        'product': product,
                        'qty': qty,
                        'subtotal_cents': subtotal
                    })
                    total_cents += subtotal

        return render_template('cart.html', items=items, total_cents=total_cents)

    @app.route('/cart/add/<int:product_id>', methods=['POST'])
    def cart_add(product_id):
        """Agrega un producto al carrito (funciona con o sin login)."""
        product = Product.query.get_or_404(product_id)

        if current_user.is_authenticated:
            existing_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
            if existing_item:
                existing_item.qty += 1
            else:
                db.session.add(CartItem(user_id=current_user.id, product_id=product_id, qty=1))
            db.session.commit()
            flash("Producto agregado al carrito.", "success")
        else:
            cart = session.get('cart', {})
            cart[str(product_id)] = cart.get(str(product_id), 0) + 1
            session['cart'] = cart
            flash("Producto agregado al carrito (sesión temporal).", "success")

        return redirect(request.referrer or url_for('view_cart'))

    @app.route('/cart/remove/<int:product_id>', methods=['POST'])
    def cart_remove(product_id):
        """Elimina un producto del carrito."""
        if current_user.is_authenticated:
            item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
            if item:
                db.session.delete(item)
                db.session.commit()
        else:
            cart = _get_cart()
            if str(product_id) in cart:
                del cart[str(product_id)]
                _save_cart(cart)
        flash('Producto eliminado del carrito.', 'info')
        return redirect(url_for('view_cart'))

    @app.route('/cart/clear', methods=['POST'])
    def cart_clear():
        """Vacía el carrito completamente."""
        if current_user.is_authenticated:
            CartItem.query.filter_by(user_id=current_user.id).delete()
            db.session.commit()
        else:
            session.pop('cart', None)
        flash('Carrito vaciado.', 'info')
        return redirect(url_for('view_cart'))

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

