from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from werkzeug.utils import secure_filename
from flask_login import current_user, login_required
import os

from models import User
from billingmodels import *
from billingforms import *


# View all bills
@app.route('/view_all_bills')
def view_all_bills():
    bills = Bill.query.all()
    return render_template('billing/view_all_bills.html', bills=bills)

@app.route('/bill/create/<int:visit_id>', methods=['GET', 'POST'])
@login_required
def create_bill(visit_id):
    visit = MaintenanceVisit.query.get_or_404(visit_id)
    if not current_user.is_admin and visit.customer_id != current_user.id:
        flash("Access restricted.")
        return redirect(url_for('home'))

    form = AddLineItemForm()
    bill = Bill.query.filter_by(visitID=visit_id).first()

    # If no bill exists for this visit, create one with a default line item
    if not bill:
        bill = Bill(visitID=visit_id, Notes="")
        db.session.add(bill)
        db.session.commit()

        # Add the default maintenance visit line item
        default_item = BillLineItem(
            BillID=bill.BillID,
            Description="Maintenance Visit",
            Quantity=1,
            UnitPrice=55.00
        )
        db.session.add(default_item)
        db.session.commit()
        flash("Default line item added for maintenance visit.", "success")

    # Handle form submission to add more line items
    if form.validate_on_submit():
        line_item = BillLineItem(
            BillID=bill.BillID,
            Description=form.description.data,
            Quantity=form.quantity.data,
            UnitPrice=form.unit_price.data
        )
        db.session.add(line_item)
        db.session.commit()
        flash("Line item added successfully.", "success")

        # Calculate the TotalAmount by summing up all line item TotalPrices
        total_amount = sum(item.TotalPrice for item in bill.line_items)
        bill.TotalAmount = total_amount

        # Commit the changes to update the TotalAmount in the database
        db.session.commit()

    # Get the updated bill with all line items
    bill = Bill.query.get(bill.BillID)

    return render_template(
        'billing/create_bill_with_items.html',
        form=form,
        bill=bill,
        visit=visit
    )



# Mark bill as paid
@app.route('/bill/<int:bill_id>/mark-paid', methods=['POST'])
def mark_bill_paid(bill_id):
    bill = Bill.query.get_or_404(bill_id)
    bill.is_paid = True
    bill.paid_at = datetime.utcnow()
    db.session.commit()
    flash('Bill marked as paid.', 'success')
    return redirect(url_for('billing/billing.view_bills'))
#########################################################33
# --- Customer Management ---
#########################################################
@app.route('/customer_management', methods=['GET'])
@login_required
def customer_management():
    if not current_user.is_admin:
        flash("Access restricted to administrators.")
        return redirect(url_for('home'))
    
    maintenance_customers = User.query.filter_by(is_maintenance=True).all()
    return render_template('billing/customer_management.html', maintenance_customers=maintenance_customers)

@app.route('/add_maintenance_customer', methods=['GET'])
@login_required
def add_maintenance_customer():
    if not current_user.is_admin:
        flash("Access restricted to administrators.")
        return redirect(url_for('home'))
    
    return render_template('billing/add_maintenance_customer.html')

import os

@app.route('/submit_maintenance_customer', methods=['POST'])
@login_required
def submit_maintenance_customer():
    data = request.get_json()
    customer_id = data.get('customer_id')

    if not customer_id:
        return jsonify({'success': False, 'message': 'Invalid customer ID.'}), 400

    customer = User.query.get(customer_id)
    if not customer:
        return jsonify({'success': False, 'message': 'Customer not found.'}), 404

    # Update the is_maintenance flag
    customer.is_maintenance = True
    db.session.commit()

    # Create a unique folder for the customer
    
    folder_path = os.path.join('static', 'uploads', 'billing', customer.maintenance_folder_path)

    try:
        os.makedirs(folder_path, exist_ok=True) # exists_ok=True will check to see if the folder already exists, and if it does don't do anything
    except Exception as e:
        return jsonify({'success': False, 'message': f"Error creating folder: {str(e)}"}), 500

    return jsonify({'success': True, 'message': 'Customer updated and folder created successfully.'})



@app.route('/search_customers', methods=['GET'])
@login_required
def search_customers():
    query = request.args.get('query', '')
    if not query:
        return jsonify([])
    
    customers = User.query.filter(
        (User.first_name.ilike(f'%{query}%')) | (User.last_name.ilike(f'%{query}%'))
    ).all()

    results = [{
        'id': customer.user_id,
        'first_name': customer.first_name,
        'last_name': customer.last_name,
        'phone': customer.phone_number,
        'email': customer.email
    } for customer in customers]
    return jsonify(results)


###############################################
# --- Create Maintenance Visit ---
###############################################
@app.route('/create_maintenance_visit', methods=['GET', 'POST'])
@login_required
def create_maintenance_visit():
    if not current_user.is_admin:
        flash("Access restricted to administrators.")
        return redirect(url_for('home'))
    
    form = MaintenanceVisitForm()
    form.customer_id.choices = [
        (user.user_id, f"{user.first_name} {user.last_name}")
        for user in User.query.filter_by(is_maintenance=True).all()
    ]
    
    if form.validate_on_submit():
        customer = User.query.filter_by(user_id = form.customer_id.data).first()
        # save images
        imagepre = form.before_picture.data
        imagepost = form.after_picture.data
        if imagepre:
            filename = secure_filename(imagepre.filename)
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'],'billing',customer.maintenance_folder_path, filename)
            imagepre.save(upload_path)
            imagepre_url = f"uploads/billing/{customer.maintenance_folder_path}/{filename}" 
        else:
            imagepre_url = None
        if imagepost:
            filename = secure_filename(imagepost.filename)
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'],'billing',customer.maintenance_folder_path, filename)
            imagepost.save(upload_path)
            imagepost_url = f"uploads/billing/{customer.maintenance_folder_path}/{filename}" 
        else:
            imagepost_url = None
        
        visit = MaintenanceVisit(
            customer_id=form.customer_id.data,
            before_picture=imagepre_url,
            ammonia=form.ammonia.data,
            nitrite=form.nitrite.data,
            nitrate=form.nitrate.data,
            ph=form.ph.data,
            phosphates=form.phosphates.data,
            calcium=form.calcium.data,
            magnesium=form.magnesium.data,
            alkalinity=form.alkalinity.data,
            notes=form.notes.data,
            recommendations=form.recommendations.data,
            after_picture=imagepost_url
        )
        db.session.add(visit)
        db.session.commit()
        flash("Maintenance visit created.")
        return redirect(url_for('create_bill', visit_id=visit.visit_id))

    if not form.validate_on_submit():
        print(form.errors)
    return render_template('billing/create_maintenance_visit.html', form=form)

# --- View Maintenance Logs ---
@app.route('/view_maintenance_logs/<int:customer_id>', methods=['GET'])
@login_required
def view_maintenance_logs(customer_id):
    if not (current_user.is_admin or current_user.id == customer_id):
        flash("Access restricted.")
        return redirect(url_for('home'))
    
    visits = MaintenanceVisit.query.filter_by(customer_id=customer_id).order_by(MaintenanceVisit.date_of_visit.desc()).all()
    customer = User.query.get_or_404(customer_id)
    return render_template('billing/view_maintenance_logs.html', visits=visits, customer=customer)

# --- View Maintenance Report ---
@app.route('/maintenance_report/<int:visit_id>', methods=['GET'])
@login_required
def maintenance_report(visit_id):
    visit = MaintenanceVisit.query.get_or_404(visit_id)
    if not (current_user.is_admin or visit.customer_id == current_user.id):
        flash("Access restricted.")
        return redirect(url_for('home'))
    
    return render_template('billing/maintenance_report.html', visit=visit)

@app.route('/generate_monthly_bills', methods=['POST'])
@login_required
def generate_monthly_bills():
    if not current_user.is_admin:
        flash("Access restricted.")
        return redirect(url_for('home'))
    
    # Logic for generating and sending bills goes here.
    # This will involve iterating through maintenance visits in the current month and creating summary reports.
    flash("Monthly bills generated and emailed.")
    return redirect(url_for('billing/customer_management'))
