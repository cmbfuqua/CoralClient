from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from datetime import datetime
from . import admin_bp
from .forms import CreateOrderForm
from ..extensions import db
from ..models import User, Role, ConsignmentProduct, Order
from ..utils.utility_functions import (send_order_notification, send_dropoff_notification, 
                                       send_pickup_notification, send_cancellation_notification, admin_required)
from ..utils.gcs_utils import delete_image_from_gcs

@admin_bp.route('/manage_products')
@login_required
@admin_required
def manage_products():
    products = ConsignmentProduct.query.options(
        joinedload(ConsignmentProduct.seller),
        joinedload(ConsignmentProduct.item_type)
    ).all()
    return render_template('manage_products.html', products=products)

@admin_bp.route('/update_featured/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def update_featured(product_id):
    data = request.get_json()
    featured = data.get('featured')
    if featured is None:
        return jsonify({'error': 'Invalid data'}), 400
    product = ConsignmentProduct.query.get_or_404(product_id)
    product.featured = bool(featured)
    db.session.commit()
    return jsonify({'message': 'Featured status updated successfully.'})

@admin_bp.route('/update_user_role/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def update_user_role(user_id):
    user = User.query.get_or_404(user_id)
    new_role_id = request.form.get('role')
    new_role = Role.query.get(new_role_id)
    if not new_role:
        flash('Invalid role selected.', 'danger')
        return redirect(url_for('admin.manage_users'))
    user.role = new_role
    db.session.commit()
    flash(f"Updated {user.username}'s role to {new_role.name}.", 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/manage_users', methods=['GET'])
@login_required
@admin_required
def manage_users():
    users = User.query.order_by(User.first_name, User.last_name).all()
    roles = Role.query.all()
    return render_template('manage_users.html', users=users, roles=roles)

@admin_bp.route('/user/<int:user_id>/edit', methods=['GET'])
@login_required
@admin_required
def edit_user_admin(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('edit_user_admin.html', user=user)

@admin_bp.route('/user/<int:user_id>/update', methods=['POST'])
@login_required
@admin_required
def update_user(user_id):
    user = User.query.filter_by(user_id = user_id).first()
    user.first_name = request.form['first_name']
    user.last_name = request.form['last_name']
    user.dob = request.form['dob']
    user.phone_number = request.form['phone_number']
    user.notes = request.form['notes']
    db.session.commit()
    flash('User profile updated successfully.', 'success')
    return redirect(url_for('admin.edit_user_admin', user_id=user_id))

@admin_bp.route('/user/<int:user_id>/update-credit', methods=['POST'])
@login_required
@admin_required
def update_in_store_credit(user_id):
    user = User.query.get_or_404(user_id)
    credit_change = float(request.form['credit_change'])
    user.in_store_credit += credit_change
    db.session.commit()
    flash(f"In-store credit updated successfully. New balance: ${user.in_store_credit:.2f}", 'success')
    return redirect(url_for('admin.edit_user_admin', user_id=user_id))

@admin_bp.route('/admin/cleanup', methods=['GET'])
@login_required
@admin_required
def cleanup_page():
    return render_template('cleanup.html')

@admin_bp.route('/admin/cleanup_orders', methods=['POST'])
@login_required
@admin_required
def cleanup_orders():
    confirmation_text = request.form.get('confirmation_text')
    if confirmation_text != "I Know What I am doing":
        return jsonify({"success": False, "message": "Incorrect confirmation text."})
    orders_to_delete = Order.query.filter(Order.order_status.in_(['C', 'X'])).all()
    deleted_count = 0
    for order in orders_to_delete:
        product = order.product
        if product and product.image_url:
            delete_image_from_gcs(product.image_url)
        if product:
            db.session.delete(product)
        db.session.delete(order)
        deleted_count += 1
    db.session.commit()
    return jsonify({"success": True, "message": f"Cleanup completed. {deleted_count} orders deleted."})

@admin_bp.route('/create_order/<int:product_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def create_order(product_id):
    form = CreateOrderForm()
    product = ConsignmentProduct.query.get_or_404(product_id)
    buyers = User.query.all()
    form.buyer_id.choices = [(buyer.user_id, f"{buyer.first_name} {buyer.last_name}") for buyer in buyers]
    if form.validate_on_submit():
        buyer_id = form.buyer_id.data
        buyer = User.query.get(buyer_id)
        order = Order(product_id=product.product_id, seller_id=product.seller_id, buyer_id=buyer_id, order_status='IP')
        db.session.add(order)
        product.order_status = 'IP'
        db.session.commit()
        send_order_notification(product.seller.email, product, order.order_id, buyer.first_name, buyer.last_name)
        flash('Order created successfully.', 'success')
        return redirect(url_for('admin.order_status', order_id=order.order_id))
    return render_template('create_order.html', product=product, form=form)

@admin_bp.route('/search_buyer', methods=['GET'])
@login_required
@admin_required
def search_buyer():
    first_name = request.args.get('first_name', '').strip()
    last_name = request.args.get('last_name', '').strip()
    seller_id = request.args.get('seller_id')
    if not first_name and not last_name:
        return jsonify([])
    buyers = User.query.filter((User.first_name.ilike(f'%{first_name}%')) & (User.last_name.ilike(f'%{last_name}%')) & (User.user_id != seller_id)).all()
    return jsonify([{'user_id': b.user_id, 'first_name': b.first_name, 'last_name': b.last_name, 'email': b.email, 'phone_number': b.phone_number} for b in buyers])

@admin_bp.route('/order_status/<int:order_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def order_status(order_id):
    order = Order.query.get_or_404(order_id)
    product = order.product
    buyer = order.buyer
    seller = order.seller
    if request.method == 'POST':
        if 'set_dropoff' in request.form:
            order.product_dropoff = datetime.now()
            db.session.commit()
            send_dropoff_notification(buyer, product, seller, order)
        elif 'set_pickup' in request.form:
            order.product_pickup = datetime.now()
            order.order_status = 'C'
            product.order_status = 'C'
            db.session.commit()
            send_pickup_notification(buyer, product, seller, order)
        elif 'payment_status' in request.form:
            order.payment_status = request.form['payment_status']
            db.session.commit()
        elif 'delete_order' in request.form:
            order.order_status = 'X'
            product.order_status = None
            db.session.commit()
            send_cancellation_notification(buyer, product, seller, order)
            flash('Order canceled.', 'danger')
            return redirect(url_for('admin.all_orders'))
    return render_template('order_status.html', order=order, product=product, buyer=buyer, seller=seller)

@admin_bp.route('/orders', methods=['GET'])
@login_required
@admin_required
def all_orders():
    all_orders_data = Order.query.options(joinedload(Order.product), joinedload(Order.buyer), joinedload(Order.seller)).all()
    orders = {
        'IP': [o for o in all_orders_data if o.order_status == 'IP'],
        'C': [o for o in all_orders_data if o.order_status == 'C'],
        'X': [o for o in all_orders_data if o.order_status == 'X'],
    }
    return render_template('all_orders.html', orders=orders)
