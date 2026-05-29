from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import current_user, login_required
from sqlalchemy.orm import joinedload
from io import BytesIO
from datetime import datetime, timedelta
import requests
from concurrent.futures import ThreadPoolExecutor
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from flask_mail import Message
import os

from ..extensions import db, mail
from ..models import User, Bill, MaintenanceVisit, BillLineItem, ChemicalRanges
from .forms import AddLineItemForm, MaintenanceVisitForm
from ..utils.gcs_utils import upload_image_to_gcs
from ..utils.utility_functions import admin_required

billing_bp = Blueprint('billing', __name__)

@billing_bp.route('/generate_invoices_all/')
@login_required
@admin_required
def generate_invoices_all():
    month = request.args.get('month')
    month = int(month)
    one_year_ago = datetime.now() - timedelta(days=365)
    bills = Bill.query.filter(
        db.func.extract('month', Bill.CreatedAt) == month,
        Bill.IsPaid == False,
        Bill.CreatedAt >= one_year_ago
    ).all()

    customer_bills = {}
    for bill in bills:
        customer = bill.visit.customer
        if customer.user_id not in customer_bills:
            customer_bills[customer.user_id] = {"customer": customer, "bills": []}
        customer_bills[customer.user_id]["bills"].append(bill)

    def process_customer(app_instance, data):
        with app_instance.app_context():
            customer = data["customer"]
            customer_name = f"{customer.first_name} {customer.last_name}"
            file_name = f"{customer_name}_{month}.pdf"
            pdf_path = create_pdf(data["bills"], customer_name, file_name)
            send_email("Your Monthly Invoice", customer.email, pdf_path)
            return {"customer_name": customer_name, "customer_email": customer.email}

    success_messages = []
    app_instance = current_app._get_current_object()
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_customer, app_instance, data) for customer_id, data in customer_bills.items()]
        for future in futures:
            success_messages.append(future.result())

    now = datetime.now().date()
    start_of_month = now.replace(day=1)
    bills = Bill.query.all()
    unpaid_this_month = [bill for bill in bills if not bill.IsPaid and bill.CreatedAt >= start_of_month]
    paid_this_month = [bill for bill in bills if bill.IsPaid and bill.CreatedAt >= start_of_month]
    previous_unpaid = [bill for bill in bills if not bill.IsPaid and bill.CreatedAt < start_of_month]
    previous_paid = [bill for bill in bills if bill.IsPaid and bill.CreatedAt < start_of_month]
    
    return render_template(
        'billing/view_all_bills.html', 
        success_messages=success_messages,
        unpaid_this_month=unpaid_this_month,
        paid_this_month=paid_this_month,
        previous_unpaid=previous_unpaid,
        previous_paid=previous_paid
    )

@billing_bp.route('/generate_invoices_customer/<int:customer_id>')
@login_required
@admin_required
def generate_invoices_customer(customer_id):
    month = request.args.get('month')
    month = int(month)
    one_year_ago = datetime.now() - timedelta(days=365)
    bills = (
        db.session.query(Bill)
        .join(MaintenanceVisit)
        .filter(
            db.func.extract('month', Bill.CreatedAt) == month,
            MaintenanceVisit.customer_id == customer_id,
            Bill.IsPaid == False,
            Bill.CreatedAt >= one_year_ago
        )
        .options(joinedload(Bill.visit))
        .all()
    )

    customer = User.query.get_or_404(customer_id)
    customer_name = f"{customer.first_name} {customer.last_name}"
    file_name = f"{customer_name}_{month}.pdf"
    pdf_path = create_pdf(bills, customer_name, file_name)
    send_email("Your Monthly Invoice", customer.email, pdf_path)

    success_message = {"pdf_name": file_name, "customer_name": customer_name, "customer_email": customer.email}
    
    return render_template('billing/view_maintenance_logs.html', 
                           visits=MaintenanceVisit.query.filter_by(customer_id=customer_id).order_by(MaintenanceVisit.date_of_visit.desc()).all(), 
                           customer=customer, 
                           success_message=success_message)

@billing_bp.route('/view_all_bills')
@login_required
def view_all_bills():
    now = datetime.now().date()
    start_of_month = now.replace(day=1)
    
    if current_user.is_admin:
        bills = Bill.query.order_by(Bill.CreatedAt.desc()).all()
    else:
        bills = Bill.query.join(Bill.visit).filter(MaintenanceVisit.customer_id == current_user.user_id).order_by(Bill.CreatedAt.desc()).all()
            
    unpaid_this_month = [bill for bill in bills if not bill.IsPaid and bill.CreatedAt >= start_of_month]
    paid_this_month = [bill for bill in bills if bill.IsPaid and bill.CreatedAt >= start_of_month]
    previous_unpaid = [bill for bill in bills if not bill.IsPaid and bill.CreatedAt < start_of_month]
    previous_paid = [bill for bill in bills if bill.IsPaid and bill.CreatedAt < start_of_month]
    
    return render_template(
        'billing/view_all_bills.html',
        unpaid_this_month=unpaid_this_month,
        paid_this_month=paid_this_month,
        previous_unpaid=previous_unpaid,
        previous_paid=previous_paid
    )

@billing_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    return render_template('billing/basebilling.html')

@billing_bp.route('/bill/create/<int:visit_id>', methods=['GET', 'POST'])
@login_required
def create_bill(visit_id):
    visit = MaintenanceVisit.query.get_or_404(visit_id)
    if not current_user.is_admin and visit.customer_id != current_user.user_id:
        flash("Access restricted.")
        return redirect(url_for('main.home'))

    form = AddLineItemForm()
    bill = Bill.query.filter_by(visitID=visit_id).first()

    if not bill:
        bill = Bill(visitID=visit_id, Notes="")
        db.session.add(bill)
        db.session.commit()

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

        tax = sum(float(item.TotalPrice) for item in bill.line_items if 'lean' not in str(item.Description).lower()) * .06
        subtotal = sum(float(item.TotalPrice) for item in bill.line_items)
        bill.TotalAmount = tax + float(subtotal)
        bill.Tax = tax
        bill.SubTotal = subtotal

        if request.form.get('mark_as_paid'):
            bill.IsPaid = 1
        else:
            bill.IsPaid = 0
        db.session.commit()

    tax = sum(float(item.TotalPrice) for item in bill.line_items if 'lean' not in str(item.Description).lower()) * .06
    subtotal = sum(float(item.TotalPrice) for item in bill.line_items)
    bill.TotalAmount = tax + float(subtotal)
    bill.Tax = tax
    bill.SubTotal = subtotal
    db.session.commit()

    return render_template('billing/create_bill_with_items.html', form=form, bill=bill, visit=visit)

@billing_bp.route('/process_bill_status/<int:bill_id>', methods=['POST'])
@login_required
def process_bill_status(bill_id):
    bill = Bill.query.get_or_404(bill_id)
    if request.form.get('mark_as_paid'):
        bill.IsPaid = 1
        db.session.commit()

    customer = User.query.get_or_404(bill.visit.customer_id)
    customer_name = f"{customer.first_name} {customer.last_name}"
    file_name = f"{customer_name}.pdf"
    bills = Bill.query.filter_by(BillID=bill_id).all()
    pdf_path = create_pdf(bills, customer_name, file_name)
    send_email("Corals4Cheap Visit Invoice", customer.email, pdf_path)
    return redirect(url_for('billing.create_maintenance_visit'))

@billing_bp.route('/bill/<int:bill_id>/mark-paid', methods=['POST'])
@login_required
@admin_required
def mark_bill_paid(bill_id):
    bill = Bill.query.get_or_404(bill_id)
    bill.IsPaid = True
    bill.PaidAt = datetime.utcnow()
    db.session.commit()
    flash('Bill marked as paid.', 'success')
    return redirect(url_for('billing.view_all_bills'))

@billing_bp.route('/customer_management', methods=['GET'])
@login_required
@admin_required
def customer_management():
    maintenance_customers = User.query.filter_by(is_maintenance=True).all()
    return render_template('billing/customer_management.html', maintenance_customers=maintenance_customers)

@billing_bp.route('/add_maintenance_customer', methods=['GET'])
@login_required
@admin_required
def add_maintenance_customer():
    return render_template('billing/add_maintenance_customer.html')

@billing_bp.route('/submit_maintenance_customer', methods=['POST'])
@login_required
@admin_required
def submit_maintenance_customer():
    data = request.get_json()
    customer_id = data.get('customer_id')
    if not customer_id:
        return jsonify({'success': False, 'message': 'Invalid customer ID.'}), 400
    customer = User.query.get(customer_id)
    if not customer:
        return jsonify({'success': False, 'message': 'Customer not found.'}), 404
    customer.is_maintenance = True
    db.session.commit()
    return jsonify({'success': True, 'message': 'Customer updated and folder created successfully.'})

@billing_bp.route('/remove_maintenance_customer', methods=['POST'])
@login_required
@admin_required
def remove_maintenance_customer():
    data = request.get_json()
    customer_id = data.get('customer_id')
    if not customer_id:
        return jsonify({'success': False, 'message': 'Invalid customer ID.'}), 400
    customer = User.query.get(customer_id)
    if not customer:
        return jsonify({'success': False, 'message': 'Customer not found.'}), 404
    customer.is_maintenance = False
    db.session.commit()
    return jsonify({'success': True, 'message': 'Customer removed from maintenance successfully.'})

@billing_bp.route('/search_customers', methods=['GET'])
@login_required
def search_customers():
    query = request.args.get('query', '')
    if not query:
        return jsonify([])
    customers = User.query.filter((User.first_name.ilike(f'%{query}%')) | (User.last_name.ilike(f'%{query}%'))).all()
    results = [{'id': c.user_id, 'first_name': c.first_name, 'last_name': c.last_name, 'phone': c.phone_number, 'email': c.email} for c in customers]
    return jsonify(results)

@billing_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin.manage_users'))

@billing_bp.route('/delete_bill/<int:billID>', methods=['POST'])
@login_required
@admin_required
def delete_bill(billID):
    bill = Bill.query.get(billID)
    if not bill:
        return jsonify({'message': 'no bill found'})
    db.session.delete(bill)
    db.session.delete(bill.visit)
    db.session.commit()
    return redirect(url_for('billing.view_all_bills'))

@billing_bp.route('/create_maintenance_visit', methods=['GET', 'POST'])
@login_required
@admin_required
def create_maintenance_visit():
    form = MaintenanceVisitForm()
    form.customer_id.choices = [(user.user_id, f"{user.first_name} {user.last_name}") for user in User.query.filter_by(is_maintenance=True).all()]
    if form.validate_on_submit():
        customer = User.query.filter_by(user_id=form.customer_id.data).first()
        imagepre = form.before_picture.data
        imagepost = form.after_picture.data
        imagepre_url = None
        imagepost_url = None
        if imagepre:
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], customer.maintenance_folder_path, 'billing', 'images')
            imagepre_url = upload_image_to_gcs(upload_path, imagepre.filename, imagepre)
        if imagepost:
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], customer.maintenance_folder_path, 'billing', 'images')
            imagepost_url = upload_image_to_gcs(upload_path, imagepost.filename, imagepost)
        
        visit = MaintenanceVisit(
            customer_id=form.customer_id.data, before_picture=imagepre_url, ammonia=form.ammonia.data,
            nitrite=form.nitrite.data, nitrate=form.nitrate.data, ph=form.ph.data, phosphates=form.phosphates.data,
            calcium=form.calcium.data, magnesium=form.magnesium.data, alkalinity=form.alkalinity.data,
            notes=form.notes.data, recommendations=form.recommendations.data, after_picture=imagepost_url
        )
        db.session.add(visit)
        db.session.commit()
        bill = Bill(visitID=visit.visit_id, IsPaid=1 if request.form.get('mark_as_paid') else 0)
        db.session.add(bill)
        db.session.commit()
        flash("Maintenance visit created and bill processed.")
        return redirect(url_for('billing.create_bill', visit_id=visit.visit_id))
    return render_template('billing/create_maintenance_visit.html', form=form)

@billing_bp.route('/view_maintenance_logs/<int:customer_id>', methods=['GET'])
@login_required
def view_maintenance_logs(customer_id):
    if not (current_user.is_admin or current_user.user_id == customer_id):
        flash("Access restricted.")
        return redirect(url_for('main.home'))
    visits = MaintenanceVisit.query.filter_by(customer_id=customer_id).order_by(MaintenanceVisit.date_of_visit.desc()).all()
    customer = User.query.get_or_404(customer_id)
    return render_template('billing/view_maintenance_logs.html', visits=visits, customer=customer)

@billing_bp.route('/maintenance_report/<int:visit_id>', methods=['GET'])
@login_required
def maintenance_report(visit_id):
    visit = MaintenanceVisit.query.get_or_404(visit_id)
    chemranges = ChemicalRanges.query.all()
    if not (current_user.is_admin or visit.customer_id == current_user.user_id):
        flash("Access restricted.")
        return redirect(url_for('main.home'))
    return render_template('billing/maintenance_report.html', visit=visit, chemranges=chemranges)

def create_pdf(bills, customer_name, file_name):
    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
    pdf.setTitle(f"Invoice - {customer_name}")
    pdf.drawImage("https://storage.googleapis.com/corals4cheapbuckets/logo.png", 50, 750, width=200, height=50)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, 700, f"Invoices - {customer_name}")
    y_position = 650
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y_position, "Date")
    pdf.drawString(150, y_position, "Bill ID")
    pdf.drawString(250, y_position, "Total Amount")
    y_position -= 20
    total_amount = 0
    pdf.setFont("Helvetica", 10)
    for bill in bills:
        pdf.drawString(50, y_position, str(bill.CreatedAt))
        pdf.drawString(150, y_position, str(bill.BillID))
        pdf.drawString(250, y_position, f"${bill.TotalAmount:.2f}")
        total_amount += bill.TotalAmount
        y_position -= 20
        pdf.setFont("Helvetica-Bold", 9)
        pdf.drawString(70, y_position, "Line Items:")
        y_position -= 15
        pdf.setFont("Helvetica", 9)
        pdf.drawString(70, y_position, "• Description")
        pdf.drawString(220, y_position, "Quantity")
        pdf.drawString(300, y_position, "Unit Price")
        pdf.drawString(400, y_position, "Total Price")
        y_position -= 15
        for item in bill.line_items:
            pdf.setFont("Helvetica", 9)
            pdf.drawString(70, y_position, f"• {item.Description}")
            pdf.drawString(220, y_position, str(item.Quantity))
            pdf.drawString(300, y_position, f"${item.UnitPrice:.2f}")
            pdf.drawString(400, y_position, f"${item.TotalPrice:.2f}")
            y_position -= 15
            if y_position < 50:
                pdf.showPage()
                y_position = 750
        y_position -= 10
        pdf.setFont("Helvetica", 10)
        if y_position < 50:
            pdf.showPage()
            y_position = 750
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y_position - 20, f"Total Amount: ${total_amount:.2f}")
    pdf.save()
    pdf_buffer.seek(0)
    user_folder = customer_name.replace(" ", "_")
    pdf_blob = upload_image_to_gcs(user_folder, file_name, pdf_buffer)
    return pdf_blob

def send_email(subject, recipient, file_path):
    response = requests.get(file_path)
    if response.status_code == 200:
        pdf_data = response.content
        msg = Message(subject, recipients=[recipient])
        msg.body = "Please find attached your invoice."
        msg.attach("invoice.pdf", "application/pdf", pdf_data)
        mail.send(msg)
    else:
        raise Exception(f"Failed to fetch PDF from GCS: {response.status_code}")
