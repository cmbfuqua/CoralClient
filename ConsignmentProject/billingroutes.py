from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required

from models import User
from billingmodels import *
from billingforms import *


# View all bills
@app.route('/view_all_bills')
def view_all_bills():
    bills = Bill.query.all()
    return render_template('billing/view_all_bills.html', bills=bills)

# Create a new bill for a maintenance visit
@app.route('/bill/create/<int:visit_id>', methods=['GET', 'POST'])
def create_bill(visit_id):
    form = CreateBillForm()
    if form.validate_on_submit():
        bill = Bill(visit_id=visit_id, notes=form.notes.data)
        db.session.add(bill)
        db.session.commit()
        flash('Bill created successfully.', 'success')
        return redirect(url_for('billing/add_line_item', bill_id=bill.id))
    return render_template('billing/create_bill.html', form=form)

# Add line items to a bill
@app.route('/bill/<int:bill_id>/add-line-item', methods=['GET', 'POST'])
def add_line_item(bill_id):
    form = AddLineItemForm()
    if form.validate_on_submit():
        line_item = BillLineItem(
            bill_id=bill_id,
            description=form.description.data,
            quantity=form.quantity.data,
            unit_price=form.unit_price.data
        )
        db.session.add(line_item)
        db.session.commit()
        flash('Line item added successfully.', 'success')
    bill = Bill.query.get_or_404(bill_id)
    return render_template('billing/add_line_item.html', form=form, bill=bill)

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

    return jsonify({'success': True, 'message': 'Customer updated successfully.'})


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
        visit = MaintenanceVisit(
            customer_id=form.customer_id.data,
            before_picture=form.before_picture.data.filename,
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
            after_picture=form.after_picture.data.filename
        )
        db.session.add(visit)
        db.session.commit()
        flash("Maintenance visit created.")
        mcustomers = User.query.filter_by(is_maintenance=True).all()
        return render_template('billing/customer_management.html',maintenance_customer = mcustomers)
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
