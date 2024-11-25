from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_mail import Mail, Message
from flask_bcrypt import Bcrypt
from config import Config
from models import User, Role, ConsignmentProduct, Order
from forms import RegistrationForm, LoginForm, ConsignmentForm
from DB import db, app
# Initialize Flask app

mail = Mail(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Function to validate DB connection
def validate_db_connection():
    """
    Validate the connection to the database.
    """
    try:
        with app.app_context():
            # Attempt to connect to the database
            print("Database connection successful.")
    except Exception as e:
        print(f"Error: Unable to connect to the database.\n{e}")
        exit(1)  # Exit the program if the database is not reachable

validate_db_connection()

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home route
@app.route('/')
def home():
    print('Home Accessed')
    featured_products = ConsignmentProduct.query.filter_by(featured=True).all()
    orders = Order.query.all()

    # Handle empty lists if no products or orders are found
    if not featured_products:
        featured_products = []  # Provide an empty list if no products

    if not orders:
        orders = []  # Provide an empty list if no orders

    return render_template('home.html', featured_products=featured_products, orders=orders)


# User registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user_role = Role.query.filter_by(name='user').first()
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, role=user_role)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)

# User logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/fish')
def fish():
    # Query the database for all fish (or products)
    fish = ConsignmentProduct.query.filter_by(category="Fish").all()  # Replace with actual query if needed
    return render_template('fish.html', fish=fish)

# Consignment management for sellers
@app.route('/consignment', methods=['GET', 'POST'])
@login_required
def consignment():
    if current_user.role.name not in ['seller', 'admin']:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))
    
    form = ConsignmentForm()
    if form.validate_on_submit():
        product = ConsignmentProduct(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            item_type_id=form.item_type.data,
            seller_id=current_user.user_id
        )
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('consignment'))

    user_products = ConsignmentProduct.query.filter_by(seller_id=current_user.user_id).all()
    return render_template('consignment.html', form=form, user_products=user_products)

# Admin functionality for managing consignments
@app.route('/manage_products')
@login_required
def manage_products():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))

    products = ConsignmentProduct.query.all()
    return render_template('manage_products.html', products=products)

# Creating an order (admin only)
@app.route('/create_order/<int:product_id>', methods=['POST'])
@login_required
def create_order(product_id):
    if not current_user.is_admin:
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('home'))
    
    product = ConsignmentProduct.query.get_or_404(product_id)
    buyer_id = request.form.get('buyer_id')

    if not buyer_id:
        flash('Buyer information is required.', 'danger')
        return redirect(url_for('search'))

    order = Order(buyer_id=buyer_id, seller_id=product.seller_id, product_id=product.product_id)
    db.session.add(order)
    db.session.commit()

    # Notify the seller
    send_order_notification(product.seller.email, product)

    flash('Order created successfully and seller notified.', 'success')
    return redirect(url_for('home'))

# Account management for all users
@app.route('/account')
@login_required
def account():
    return render_template('account.html', user=current_user)

# Route for admin to upgrade users to sellers
@app.route('/upgrade_user/<int:user_id>', methods=['POST'])
@login_required
def upgrade_user(user_id):
    if not current_user.is_admin:
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('home'))
    
    user = User.query.get(user_id)
    if user.role.name == 'user':
        seller_role = Role.query.filter_by(name='seller').first()
        user.role = seller_role
        db.session.commit()
        flash(f'{user.username} has been upgraded to Seller.', 'success')
    else:
        flash('User is already a Seller or Admin.', 'info')
    
    return redirect(url_for('manage_users'))

@app.route('/corals')
def corals():
    # Query the database for all corals (or products)
    corals = ConsignmentProduct.query.all()  # Replace with actual query
    return render_template('corals.html', corals=corals)


# Admin functionality to manage users
@app.route('/manage_users')
@login_required
def manage_users():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))

    users = User.query.all()
    return render_template('manage_users.html', users=users)

def send_order_notification(buyer_email, seller_email, product_name):
    subject = f"New Order Request for {product_name}"
    sender = app.config['MAIL_DEFAULT_SENDER']
    
    msg = Message(subject, sender=sender, recipients=[seller_email])
    msg.body = f"Hello, there is a new order request for {product_name}.\n\nPlease contact the buyer at {buyer_email} to arrange the sale."
    
    mail.send(msg)

# Print out all registered routes for debugging purposes

if __name__ == '__main__':
    app.run(debug=True)
