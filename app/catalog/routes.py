import os
from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from . import catalog_bp
from .forms import ConsignmentForm
from ..extensions import db
from ..models import User, ItemType, ItemSubtype, ConsignmentProduct, Order
from ..utils.gcs_utils import upload_image_to_gcs, allowed_file

@catalog_bp.route('/corals')
def corals():
    corals = (
        ConsignmentProduct.query
        .filter(ConsignmentProduct.item_type_id == 1)
        .outerjoin(Order, Order.product_id == ConsignmentProduct.product_id)
        .filter(or_(Order.order_status != 'C', Order.order_status.is_(None)))
        .options(joinedload(ConsignmentProduct.orders))
        .all()
    )
    coral_subtypes = ItemSubtype.query.filter_by(item_type_id=1).all()
    return render_template('corals.html', corals=corals, coral_subtypes=coral_subtypes)

@catalog_bp.route('/fish')
def fish():
    fish = (
        ConsignmentProduct.query
        .filter(ConsignmentProduct.item_type_id == 2)
        .outerjoin(Order, Order.product_id == ConsignmentProduct.product_id)
        .filter(or_(Order.order_status != 'C', Order.order_status.is_(None)))
        .options(joinedload(ConsignmentProduct.orders))
        .all()
    )
    fish_subtypes = ItemSubtype.query.filter_by(item_type_id=2).order_by(ItemSubtype.name).all()
    return render_template('fish.html', fish=fish, fish_subtypes=fish_subtypes)

@catalog_bp.route('/equipment')
def equipment():
    equipment = (
        ConsignmentProduct.query
        .filter(ConsignmentProduct.item_type_id == 3)
        .filter(ConsignmentProduct.order_status != 'C')
        .all()
    )
    equipment_subtypes = ItemSubtype.query.filter_by(item_type_id=3).order_by(ItemSubtype.name).all()
    return render_template('equipment.html', equipment=equipment, equipment_subtypes=equipment_subtypes)

@catalog_bp.route('/consignment', methods=['GET', 'POST'])
@login_required
def consignment():
    if current_user.role_id not in [2, 3]:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.home'))

    form = ConsignmentForm()
    item_types = ItemType.query.all()
    form.item_type.choices = [(item.item_type_id, item.name) for item in item_types]
    subtypes = ItemSubtype.query.order_by(ItemSubtype.name).all()
    form.item_subtype.choices = [(sub.item_subtype_id, sub.name) for sub in subtypes]

    if form.validate_on_submit():
        image = form.image.data
        image_url = None
        if image:
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], current_user.maintenance_folder_path)
            image_url = upload_image_to_gcs(upload_path, image.filename, image)

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
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('catalog.consignment'))

    user_products = ConsignmentProduct.query.filter_by(seller_id=current_user.user_id).filter(ConsignmentProduct.order_status != 'C').all()
    return render_template('consignment.html', form=form, user_products=user_products)

@catalog_bp.route('/subcategories/<int:item_type_id>')
def get_subcategories(item_type_id):
    subtypes = ItemSubtype.query.filter_by(item_type_id=item_type_id).order_by(ItemSubtype.name).all()
    return jsonify([(sub.item_subtype_id, sub.name) for sub in subtypes])

@catalog_bp.route('/consignment/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    product = ConsignmentProduct.query.filter_by(product_id=item_id).first()
    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for('catalog.consignment'))

    if not (current_user.is_admin or product.seller_id == current_user.user_id):
        flash('You do not have permission to edit this item.', 'danger')
        return redirect(url_for('catalog.consignment'))

    form = ConsignmentForm(obj=product)
    item_types = ItemType.query.all()
    form.item_type.choices = [(item.item_type_id, item.name) for item in item_types]
    subtypes = ItemSubtype.query.order_by(ItemSubtype.name).all()
    form.item_subtype.choices = [(sub.item_subtype_id, sub.name) for sub in subtypes]

    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.item_type_id = form.item_type.data
        product.item_subtype_id = form.item_subtype.data

        if form.image.data:
            file = form.image.data
            if allowed_file(file.filename):
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], current_user.maintenance_folder_path)
                product.image_url = upload_image_to_gcs(upload_path, file.filename, file)
            else:
                flash('Invalid file type for image.', 'danger')
                return redirect(url_for('catalog.edit_item', item_id=item_id))

        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('catalog.consignment'))

    return render_template('edit_item.html', form=form, item=product)

@catalog_bp.route('/delete_item/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    item = ConsignmentProduct.query.get_or_404(item_id)
    if item.seller_id != current_user.user_id and not current_user.is_admin:
        flash("You do not have permission to delete this item.")
        return redirect(url_for('catalog.consignment'))
    if item.order_status != 'None':
        flash("Item cannot be deleted as it has been ordered or processed.")
        return redirect(url_for('catalog.consignment'))
    db.session.delete(item)
    db.session.commit()
    flash("Item deleted successfully.")
    return redirect(url_for('catalog.consignment'))
