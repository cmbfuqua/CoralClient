from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_mail import Mail, Message
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
from billingroutes import *

from models import *
from forms import *
from DB import db, app

import os
from datetime import datetime

# Initialize Flask app

mail = Mail(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
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
    return User.query.filter_by(user_id = (int(user_id))).first()

# Home route
@app.route('/')
def home():
    featured_products = ConsignmentProduct.query.filter_by(featured=True).all()
    orders = Order.query.all()

    # Handle empty lists if no products or orders are found
    if not featured_products:
        featured_products = []  # Provide an empty list if no products

    if not orders:
        orders = []  # Provide an empty list if no orders

    return render_template('home.html', featured_products=featured_products, orders=orders)


############################################################3
# Register, edit and login User
############################################################
# User registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user_role = Role.query.filter_by(name='user').first()
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            dob=form.dob.data,
            phone_number=form.phone_number.data,
            role=user_role,
            in_store_credit=0
        )
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/edit_user', methods=['GET', 'POST'])
@login_required
def edit_user():
    form = EditUserForm(obj=current_user)  # Pre-fill form with current user data
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.dob = form.dob.data
        current_user.phone_number = form.phone_number.data
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('home'))
    return render_template('edit_user.html', form=form)

@app.route('/user/<int:user_id>/edit', methods=['GET'])
def edit_user_admin(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('edit_user_admin.html', user=user)

@app.route('/user/<int:user_id>/update', methods=['POST'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    user.first_name = request.form['first_name']
    user.last_name = request.form['last_name']
    user.dob = request.form['dob']
    user.in_store_credit = float(request.form['in_store_credit'])
    user.phone_number = request.form['phone_number']
    db.session.commit()
    flash('User profile updated successfully.', 'success')
    return redirect(url_for('edit_user_admin', user_id=user_id))

@app.route('/user/<int:user_id>/update-credit', methods=['POST'])
def update_in_store_credit(user_id):
    user = User.query.get_or_404(user_id)
    credit_change = float(request.form['credit_change'])
    user.in_store_credit += credit_change
    db.session.commit()
    flash(f"In-store credit updated successfully. New balance: ${user.in_store_credit:.2f}", 'success')
    return redirect(url_for('edit_user_admin', user_id=user_id))

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(
            (User.email == form.username_or_email.data) | 
            (User.username == form.username_or_email.data)
        ).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username/email and password', 'danger')
    return render_template('login.html', form=form)


# User logout
@app.route('/logout')
@login_required
def logout():
    logout_user()  # Logs out the current user
    flash('You have been logged out.', 'info')  # Optional feedback message
    return redirect(url_for('home'))  # Redirect to the homepage

###############################################################
# Content pages
###############################################################
@app.route('/fish')
def fish():
    # Query the database for all fish (or products)
    fish = ConsignmentProduct.query.filter_by(item_type_id = 2).all()  # Replace with actual query if needed
    fish_subtypes = ItemSubtype.query.filter_by(item_type_id = 2).order_by(ItemSubtype.name).all()
    return render_template('fish.html', fish=fish,fish_subtypes = fish_subtypes)

@app.route('/corals')
def corals():
    # Query the database for all corals (or products)
    corals = ConsignmentProduct.query.filter_by(item_type_id = 1).all()  # Replace with actual query
    coral_subtypes = ItemSubtype.query.filter_by(item_type_id = 1).all()
    return render_template('corals.html', corals=corals,coral_subtypes = coral_subtypes)

from flask import render_template

@app.route('/about_us')
def about_us():
    return render_template('about_us.html')

@app.route('/policy')
def policy():
    return render_template('policy.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

#################################################################
# Consignment stuff
#################################################################
@app.route('/consignment', methods=['GET', 'POST'])
@login_required
def consignment():
    if current_user.role_id not in [2, 3]:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))

    form = ConsignmentForm()

    # Populate item_type choices
    item_types = ItemType.query.all()
    form.item_type.choices = [(item.item_type_id, item.name) for item in item_types]

    # Populate sub_category choices based on the selected item_type
    if form.item_type.choices:
        subtypes = ItemSubtype.query.order_by(ItemSubtype.name).all()
    else:
        subtypes = []

    form.item_subtype.choices = [(sub.item_subtype_id, sub.name) for sub in subtypes]
    if form.validate_on_submit():
        image = form.image.data
        if image:
            filename = secure_filename(image.filename)
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(upload_path)
            image_url = f"uploads/{filename}"  # Store the relative path
        else:
            image_url = None


        product = ConsignmentProduct(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            item_type_id=form.item_type.data,
            item_subtype_id=form.item_subtype.data,
            image_url=image_url,
            seller_id=current_user.user_id,
            order_status='None'
        )
        print('saving product')
        db.session.add(product)
        db.session.commit()

        flash('Product added successfully!', 'success')
        return redirect(url_for('consignment'))

    user_products = ConsignmentProduct.query.filter((ConsignmentProduct.seller_id == current_user.user_id) &
                                                    ((ConsignmentProduct.order_status == 'IP') | (ConsignmentProduct.order_status =='None'))).all()
    return render_template('consignment.html', form=form, user_products=user_products)

@app.route('/subcategories/<int:item_type_id>')
def get_subcategories(item_type_id):
    subtypes = ItemSubtype.query.filter_by(item_type_id=item_type_id).order_by(ItemSubtype.name).all()
    return jsonify([(sub.item_subtype_id, sub.name) for sub in subtypes])

@app.route('/consignment/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    product = ConsignmentProduct.query.filter_by(product_id=item_id).first()

    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for('consignment'))

    if not (current_user.is_admin or product.seller_id == current_user.user_id):
        flash('You do not have permission to edit this item.', 'danger')
        return redirect(url_for('consignment'))

    # Initialize the form
    form = ConsignmentForm(obj=product)

    # Populate item_type choices
    item_types = ItemType.query.all()
    form.item_type.choices = [(item.item_type_id, item.name) for item in item_types]

    # Populate subcategory choices
    subtypes = ItemSubtype.query.order_by(ItemSubtype.name).all()
    form.item_subtype.choices = [(sub.item_subtype_id, sub.name) for sub in subtypes]

    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.item_type_id = form.item_type.data
        product.item_subtype_id = form.item_subtype.data

        # Handle image upload
        if form.image.data:
            file = form.image.data
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                product.image_url = f'static/uploads/{filename}'
            else:
                flash('Invalid file type for image.', 'danger')
                return redirect(url_for('edit_item', item_id=item_id))

        # Only admin can update 'featured'
        if current_user.role_id == 3:
            product.featured = form.featured.data

        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('consignment'))

    return render_template('edit_item.html', form=form, item=product)


@app.route('/delete_item/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    item = ConsignmentProduct.query.get_or_404(item_id)

    # Ensure the current user is the seller of the item or has admin privileges
    if item.seller_id != current_user.user_id and not current_user.is_admin:
        flash("You do not have permission to delete this item.")
        return redirect(url_for('consignment'))

    # Check the order status
    if item.order_status != 'None':
        flash("Item cannot be deleted as it has been ordered or processed.")
        return redirect(url_for('consignment'))

    # Proceed with deletion
    db.session.delete(item)
    db.session.commit()
    flash("Item deleted successfully.")
    return redirect(url_for('consignment'))


##############################################################
# Admin stuff
##############################################################
# Admin functionality for managing consignments
@app.route('/manage_products')
@login_required
def manage_products():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))

    products = ConsignmentProduct.query.all()
    return render_template('manage_products.html', products=products)

from flask import request, jsonify

@app.route('/update_featured/<int:product_id>', methods=['POST'])
def update_featured(product_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    featured = data.get('featured')

    if featured is None:
        return jsonify({'error': 'Invalid data'}), 400

    product = ConsignmentProduct.query.get_or_404(product_id)
    product.featured = bool(featured)
    db.session.commit()
    return jsonify({'message': 'Featured status updated successfully.'})


# Account management for all users
@app.route('/account')
@login_required
def account():
    return render_template('account.html', user=current_user)

# Route for admin to upgrade users to sellers
@app.route('/update_user_role/<int:user_id>', methods=['POST'])
@login_required
def update_user_role(user_id):
    if not current_user.is_admin:
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('manage_users'))

    user = User.query.get_or_404(user_id)
    new_role_id = request.form.get('role')

    # Check if the role exists
    new_role = Role.query.get(new_role_id)
    if not new_role:
        flash('Invalid role selected.', 'danger')
        return redirect(url_for('manage_users'))

    # Update the user's role
    user.role = new_role
    db.session.commit()
    flash(f"Updated {user.username}'s role to {new_role.name}.", 'success')
    return redirect(url_for('manage_users'))

# Admin functionality to manage users
@app.route('/manage_users', methods=['GET'])
@login_required
def manage_users():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))

    users = User.query.all()
    roles = Role.query.all()  # Get all roles (e.g., user, seller, admin)
    return render_template('manage_users.html', users=users, roles=roles)

###################################################
# Creating Orders
###################################################
# Creating an order (admin only)
@app.route('/create_order/<int:product_id>', methods=['GET', 'POST'])
@login_required
def create_order(product_id):

    form = CreateOrderForm()
    # Fetch product information
    product = ConsignmentProduct.query.get_or_404(product_id)

    # Ensure only admins can access
    if not current_user.is_admin:
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('home'))

    # Fetch buyers to populate the select field
    buyers = User.query.all()  # You can add filters if needed to only select buyers
    form.buyer_id.choices = [(buyer.user_id, f"{buyer.first_name} {buyer.last_name}") for buyer in buyers]

    if form.validate_on_submit():
        # Handle order creation
        buyer_id = form.buyer_id.data
        buyer = User.query.filter_by(user_id = buyer_id).first()
        # Create the order
        order = Order(
            product_id=product.product_id,
            seller_id=product.seller_id,
            buyer_id=buyer_id,
            order_status='IP'
        )
        db.session.add(order)
        product.order_status = 'IP'
        db.session.commit()
        send_order_notification(product.seller.email, product, order.order_id, buyer.first_name, buyer.last_name)

        # Notify the seller

        flash('Order created successfully and seller notified.', 'success')
        return redirect(url_for('order_status', order_id=order.order_id))

    return render_template('create_order.html', product=product, form=form)


@app.route('/search_buyer', methods=['GET'])
@login_required
def search_buyer():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized access'}), 403

    first_name = request.args.get('first_name', '').strip()
    last_name = request.args.get('last_name', '').strip()
    seller_id = request.args.get('seller_id')

    if not first_name and not last_name:
        return jsonify([])  # Return empty list if no query is provided

    # Search for users matching either the first or last name
    buyers = User.query.filter(
        (User.first_name.ilike(f'%{first_name}%')) & (User.last_name.ilike(f'%{last_name}%')) & (User.user_id != seller_id)
    ).all()

    # Return matching buyers as JSON
    return jsonify([
        {
            'user_id': buyer.user_id,
            'first_name': buyer.first_name,
            'last_name': buyer.last_name,
            'email': buyer.email,
            'phone_number':buyer.phone_number
        }
        for buyer in buyers
    ])


@app.route('/order_status/<int:order_id>', methods=['GET', 'POST'])
@login_required
def order_status(order_id):
    order = Order.query.get_or_404(order_id)
    product = ConsignmentProduct.query.get_or_404(order.product_id)
    buyer = User.query.get_or_404(order.buyer_id)
    seller = User.query.get_or_404(order.seller_id)

    if request.method == 'POST':
        # Update product dropoff
        if 'set_dropoff' in request.form:
            order.product_dropoff = datetime.now()
            db.session.commit()

            # Send email to the buyer
            send_dropoff_notification(buyer, product, seller,order)

        # Update product pickup
        elif 'set_pickup' in request.form:
            order.product_pickup = datetime.now()
            order.order_status = 'C'  # Completed
            db.session.commit()

            # Send email to buyer and seller
            send_pickup_notification(buyer, product, seller,order)

        # Update payment status
        elif 'payment_status' in request.form:
            payment_status = request.form['payment_status']
            order.payment_status = payment_status
            db.session.commit()

        # Delete order
        elif 'delete_order' in request.form:
            order.order_status = 'X'  # Canceled
            product.order_status = None
            db.session.commit()

            # Send cancellation email to seller
            send_cancellation_notification(buyer, product, seller,order)

            flash('Order canceled successfully.', 'danger')
            return redirect(url_for('all_orders'))

    return render_template('order_status.html', order=order, product=product, buyer=buyer, seller=seller)

@app.route('/orders', methods=['GET'])
@login_required
def all_orders():
    if not current_user.is_admin:
        flash('You do not have permission to view this page.', 'danger')
        return redirect(url_for('home'))

    # Fetch orders grouped by status
    orders = {
        'IP': Order.query.filter_by(order_status='IP').all(),
        'C': Order.query.filter_by(order_status='C').all(),
        'X': Order.query.filter_by(order_status='X').all(),
    }

    return render_template('all_orders.html', orders=orders)


############################################
# utility functions
############################################
def allowed_file(filename):
    
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_order_notification(seller_email, product, order_number,buyer_first_name,buyer_last_name):

    
    msg = Message(
        subject="New Order Created",
        recipients=[seller_email],
        html=render_template(
            'order_notification_email.html',  # Use an HTML template for the email body
            product=product,
            order_id=order_number,
            buyer_first_name=buyer_first_name,
            buyer_last_name=buyer_last_name,
        )
    )
    mail.send(msg)

def send_dropoff_notification(buyer, product, seller,order):
    msg = Message("Coral Dropoff Notification", recipients=[buyer.email])
    msg.html = render_template('dropoff_notification.html', buyer=buyer, product=product, seller=seller,order=order)
    mail.send(msg)

def send_pickup_notification(buyer, product, seller,order):
    msg = Message("Coral Pickup Complete", recipients=[buyer.email, seller.email])
    msg.html = render_template('pickup_notification.html', buyer=buyer, seller=seller, product=product,order=order)
    mail.send(msg)

def send_cancellation_notification(buyer, product, seller,order):
    msg = Message("Order Canceled", recipients=[buyer.email,seller.email])
    msg.html = render_template('cancellation_notification.html', seller=seller, product=product, buyer=buyer,order=order)
    mail.send(msg)


################################################
# billing
################################################
@app.route('/billing', methods=['GET'])
@login_required
def billing():
    
    return render_template('billing/basebilling.html')

if __name__ == '__main__':
    app.run(debug=True)
