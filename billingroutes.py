from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import letter
from flask_mail import Message, Mail
from reportlab.pdfgen import canvas
from sqlalchemy.orm import joinedload
from io import BytesIO
from flask_login import current_user, login_required
from google.cloud import storage

import os
from concurrent.futures import ThreadPoolExecutor
import requests
from datetime import datetime, timedelta
from utility_functions import upload_image_to_gcs 

from models import User
from billingmodels import *
from billingforms import *

mail = Mail(app)
#################################################
# Generating invoices
#################################################



@app.route('/generate_invoices_all/')
def generate_invoices_all():
    month = request.args.get('month')
    month = int(month)  # Ensure month is numeric
    one_year_ago = datetime.now() - timedelta(days=365)
    # Query the bills for the given month
    bills = Bill.query.filter(
        db.func.extract('month', Bill.CreatedAt) == month,
        Bill.IsPaid == False,
        Bill.CreatedAt >= one_year_ago
    ).all()

    # Group bills by customer
    customer_bills = {}
    for bill in bills:
        customer = bill.visit.customer
        if customer.user_id not in customer_bills:
            customer_bills[customer.user_id] = {
                "customer": customer,
                "bills": []
            }
        customer_bills[customer.user_id]["bills"].append(bill)

    def process_customer(app, data):
        """Process a single customer: generate PDF and send email."""
        with app.app_context():  # Push the application context
            customer = data["customer"]
            customer_name = f"{customer.first_name} {customer.last_name}"
            file_name = f"{customer_name}_{month}.pdf"
            pdf_path = create_pdf(data["bills"], os.path.join(app.config['UPLOAD_FOLDER'],current_user.maintenance_folder_path), file_name)

            # Send email with the invoice PDF
            send_email(
                subject="Your Monthly Invoice",
                recipient=customer.email,
                file_path=pdf_path
            )

            # Return the success message for this customer
            return {
                "customer_name": customer_name,
                "customer_email": customer.email
            }

    # Use ThreadPoolExecutor for concurrent processing
    success_messages = []
    with ThreadPoolExecutor() as executor:
        # Pass the current app explicitly to each thread
        futures = [executor.submit(process_customer, current_app._get_current_object(), data) for  customer_id, data in customer_bills.items()]
        
        # Collect results as they complete
        for future in futures:
            success_messages.append(future.result())

    # Generate summary data
    now = datetime.now().date()
    start_of_month = now.replace(day=1)
    
    # Query bills and group them
    bills = Bill.query.all()
    unpaid_this_month = [bill for bill in bills if not bill.IsPaid and bill.CreatedAt.date() >= start_of_month]
    paid_this_month = [bill for bill in bills if bill.IsPaid and bill.CreatedAt.date() >= start_of_month]
    previous_unpaid = [bill for bill in bills if not bill.IsPaid and bill.CreatedAt.date() < start_of_month]
    previous_paid = [bill for bill in bills if bill.IsPaid and bill.CreatedAt.date() < start_of_month]
    
    # Pass the success messages to the template
    return render_template(
        'billing/view_all_bills.html', 
        success_messages=success_messages,
        unpaid_this_month=unpaid_this_month,
        paid_this_month=paid_this_month,
        previous_unpaid=previous_unpaid,
        previous_paid=previous_paid
    )



@app.route('/generate_invoices_customer/<int:customer_id>')
def generate_invoices_customer(customer_id):
    month = request.args.get('month')
    month = int(month)  # Ensure month is numeric
    
    # Query for the bills based on the month and customer_id
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

    # Get the customer details
    customer = User.query.get_or_404(customer_id)
    customer_name = f"{customer.first_name} {customer.last_name}"
    file_name = f"{customer_name}_{month}.pdf"
    
    # Create the PDF and save the path
    pdf_path = create_pdf(bills, os.path.join(app.config['UPLOAD_FOLDER'],current_user.maintenance_folder_path), file_name)

    # Send the invoice PDF via email
    send_email("Your Monthly Invoice", customer.email, pdf_path)

    # Prepare success message to show on the page
    success_message = {
        "pdf_name": file_name,
        "customer_name": customer_name,
        "customer_email": customer.email
    }
    
    # Redirect back to the maintenance logs page, passing the success message
    return render_template('billing/view_maintenance_logs.html', 
                           visits=MaintenanceVisit.query.filter_by(customer_id=customer_id).order_by(MaintenanceVisit.date_of_visit.desc()).all(), 
                           customer=customer, 
                           success_message=success_message)



from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_pdf(bills, customer_name, file_name):
    """
    Generate a PDF and upload it to Google Cloud Storage.
    Args:
        bills (list): List of bill objects containing CreatedAt, BillID, and TotalAmount.
        customer_name (str): Name of the customer.
        file_name (str): Name of the PDF file (e.g., 'invoice.pdf').
    Returns:
        str: The public URL of the uploaded PDF file.
    """
    # Create an in-memory buffer for the PDF
    pdf_buffer = BytesIO()

    # Generate PDF
    pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
    pdf.setTitle(f"Invoice - {customer_name}")

    # Add a logo
    pdf.drawImage(
        "https://storage.googleapis.com/corals4cheapbuckets/logo.png",
        50, 750, width=200, height=50
    )

    # Add title
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, 700, f"Invoices - {customer_name}")

    # Table headers
    y_position = 650
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y_position, "Date")
    pdf.drawString(150, y_position, "Bill ID")
    pdf.drawString(250, y_position, "Total Amount")
    y_position -= 20

    # Add bill details with line items
    total_amount = 0
    pdf.setFont("Helvetica", 10)
    for bill in bills:
        # Add bill details
        pdf.drawString(50, y_position, str(bill.CreatedAt))
        pdf.drawString(150, y_position, str(bill.BillID))
        pdf.drawString(250, y_position, f"${bill.TotalAmount:.2f}")
        total_amount += bill.TotalAmount
        y_position -= 20

        # Add line items for the current bill
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

            # Handle page overflow
            if y_position < 50:
                pdf.showPage()
                y_position = 750

        y_position -= 10  # Add some space between bills
        pdf.setFont("Helvetica", 10)

        # Handle page overflow
        if y_position < 50:
            pdf.showPage()
            y_position = 750

    # Add total summary
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y_position - 20, f"Total Amount: ${total_amount:.2f}")

    # Finalize and save the PDF
    pdf.save()

    # Reset the buffer's position to the beginning
    pdf_buffer.seek(0)

    # Upload the PDF to Google Cloud Storage
    user_folder = customer_name.replace(" ", "_")
    pdf_blob = upload_image_to_gcs(user_folder, file_name, pdf_buffer)

    return pdf_blob


def send_email(subject, recipient, file_path):
    """
    Sends an email with the PDF attachment.
    Args:
        subject (str): Email subject.
        recipient (str): Recipient email address.
        file_path (str): Public URL or path of the PDF in GCS.
    """
    response = requests.get(file_path)
    if response.status_code == 200:
        pdf_data = response.content  # Fetch the PDF content

        msg = Message(subject, recipients=[recipient])
        msg.body = "Please find attached your invoice."
        msg.attach("invoice.pdf", "application/pdf", pdf_data)
        mail.send(msg)
    else:
        raise Exception(f"Failed to fetch PDF from GCS: {response.status_code}")




# View all bills
@app.route('/view_all_bills')
def view_all_bills():
    

    # Get current date and determine the first day of the month
    now = datetime.now().date()
    start_of_month = now.replace(day=1)
    
    # Query bills and group them
    if current_user.is_admin:
        bills = Bill.query.all()
    else:
        bills = Bill.query.join(Bill.visit).filter(MaintenanceVisit.customer_id == current_user.user_id).all()
            
    unpaid_this_month = [bill for bill in bills if not bill.IsPaid and bill.CreatedAt.date() >= start_of_month]
    paid_this_month = [bill for bill in bills if bill.IsPaid and bill.CreatedAt.date() >= start_of_month]
    previous_unpaid = [bill for bill in bills if not bill.IsPaid and bill.CreatedAt.date() < start_of_month]
    previous_paid = [bill for bill in bills if bill.IsPaid and bill.CreatedAt.date() < start_of_month]
    
    return render_template(
        'billing/view_all_bills.html',
        unpaid_this_month=unpaid_this_month,
        paid_this_month=paid_this_month,
        previous_unpaid=previous_unpaid,
        previous_paid=previous_paid
    )

@app.route('/bill/create/<int:visit_id>', methods=['GET', 'POST'])
@login_required
def create_bill(visit_id):
    visit = MaintenanceVisit.query.get_or_404(visit_id)
    if not current_user.is_admin and visit.customer_id != current_user.user_id:
        flash("Access restricted.")
        return redirect(url_for('home'))

    form = AddLineItemForm()
    bill = Bill.query.filter_by(visitID=visit_id).first()

    # If no bill exists for this visit, create one with a default line item
    if not bill:
        bill = Bill(visitID=visit_id, Notes="")
        db.session.add(bill)
        db.session.commit()
        flash("Default line item added for maintenance visit.", "success")

    # Handle form submission to add line items or update the bill
    if form.validate_on_submit():
        # Add new line item
        line_item = BillLineItem(
            BillID=bill.BillID,
            Description=form.description.data,
            Quantity=form.quantity.data,
            UnitPrice=form.unit_price.data
        )
        db.session.add(line_item)
        db.session.commit()

        flash("Line item added successfully.", "success")

        # Update TotalAmount
        tax = sum(float(item.TotalPrice) for item in bill.line_items if 'lean' not in str(item.Description).lower()) * .06
        subtotal = sum(float(item.TotalPrice) for item in bill.line_items)
        bill.TotalAmount = tax+float(subtotal)
        bill.Tax = tax
        bill.SubTotal = subtotal

        # Check if the bill is marked as paid
        if request.form.get('mark_as_paid'):
            bill.IsPaid = 1
            flash("Bill marked as Paid.", "success")
        else:
            bill.IsPaid = 0

        # Commit changes to the database
        db.session.commit()

    # Calculate total amount and ensure it's displayed correctly
    tax = sum(float(item.TotalPrice) for item in bill.line_items if 'lean' not in str(item.Description).lower()) * .06
    subtotal = sum(float(item.TotalPrice) for item in bill.line_items)
    bill.TotalAmount = tax+float(subtotal)
    bill.Tax = tax
    bill.SubTotal = subtotal
    
    db.session.commit()

    return render_template(
        'billing/create_bill_with_items.html',
        form=form,
        bill=bill,
        visit=visit
    )

@app.route('/process_bill_status/<int:bill_id>', methods=['POST'])
@login_required
def process_bill_status(bill_id):
    bill = Bill.query.get_or_404(bill_id)

    if request.form.get('mark_as_paid'):  # Checkbox is checked
        bill.IsPaid = 1
        db.session.commit()

    customer = User.query.get_or_404(bill.visit.customer_id)
    customer_name = f"{customer.first_name} {customer.last_name}"
    file_name = f"{customer_name}.pdf"

    bills = Bill.query.filter_by(BillID = bill_id).all()
    # Create the PDF and save the path
    pdf_path = create_pdf(bills, os.path.join(app.config['UPLOAD_FOLDER'],current_user.maintenance_folder_path), file_name)

    # Send the invoice PDF via email
    send_email("Corals4Cheap Visit Invoice", customer.email, pdf_path)

    return redirect(url_for('create_maintenance_visit'))  # Redirect to maintenance visit creation
    

# Mark bill as paid
@app.route('/bill/<int:bill_id>/mark-paid', methods=['POST'])
def mark_bill_paid(bill_id):
    bill = Bill.query.get_or_404(bill_id)
    bill.IsPaid = True
    bill.PaidAt = datetime.utcnow()
    db.session.commit()
    print('bill marked as paid')
    flash('Bill marked as paid.', 'success')
    return redirect(url_for('view_all_bills'))
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

    return jsonify({'success': True, 'message': 'Customer updated and folder created successfully.'})

@app.route('/remove_maintenance_customer', methods=['POST'])
@login_required
def remove_maintenance_customer():
    data = request.get_json()
    customer_id = data.get('customer_id')

    if not customer_id:
        return jsonify({'success': False, 'message': 'Invalid customer ID.'}), 400

    customer = User.query.get(customer_id)
    if not customer:
        return jsonify({'success': False, 'message': 'Customer not found.'}), 404

    # Update the is_maintenance flag
    customer.is_maintenance = False
    db.session.commit()

    return jsonify({'success': True, 'message': 'Customer removed from maintenance successfully.'})


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

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    # Find the user by ID
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Delete the user from the database
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('manage_users'))

@app.route('/delete_bill/<int:billID>',methods = ['POST'])
def delete_bill(billID):
    bill = Bill.query.get(billID)
    if not bill:
        return jsonify({'message':'no bill found'})

    
    db.session.delete(bill)
    db.session.delete(bill.visit)

    db.session.commit()
    # Query bills and group them
    now = datetime.now().date()
    start_of_month = now.replace(day=1)
    bills = Bill.query.all()
    unpaid_this_month = [bill for bill in bills if not bill.IsPaid and bill.CreatedAt.date() >= start_of_month]
    paid_this_month = [bill for bill in bills if bill.IsPaid and bill.CreatedAt.date() >= start_of_month]
    previous_unpaid = [bill for bill in bills if not bill.IsPaid and bill.CreatedAt.date() < start_of_month]
    previous_paid = [bill for bill in bills if bill.IsPaid and bill.CreatedAt.date() < start_of_month]
    
    # Pass the success messages to the template
    return render_template(
        'billing/view_all_bills.html', 
        unpaid_this_month=unpaid_this_month,
        paid_this_month=paid_this_month,
        previous_unpaid=previous_unpaid,
        previous_paid=previous_paid
    )

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
        customer = User.query.filter_by(user_id=form.customer_id.data).first()
        # Handle before and after pictures
        imagepre = form.before_picture.data
        imagepost = form.after_picture.data
        imagepre_url = None
        imagepost_url = None
        if imagepre:
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], customer.maintenance_folder_path,'billing','images')
            imagepre_url = upload_image_to_gcs(upload_path,imagepre.filename,imagepre)
        if imagepost:
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], customer.maintenance_folder_path,'billing','images')
            imagepost_url = upload_image_to_gcs(upload_path,imagepost.filename,imagepost)
        
        # Create the visit
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

        # Create the bill
        bill = Bill(
            visitID=visit.visit_id,
            IsPaid=1 if request.form.get('mark_as_paid') else 0  # Mark as Paid or Unpaid
        )
        db.session.add(bill)
        db.session.commit()
        # Handle form submission to add more line items
        

        flash("Maintenance visit created and bill processed.")
        return redirect(url_for('create_bill', visit_id=visit.visit_id))

    if not form.validate_on_submit():
        print(form.errors)
    return render_template('billing/create_maintenance_visit.html', form=form)

# --- View Maintenance Logs ---
@app.route('/view_maintenance_logs/<int:customer_id>', methods=['GET'])
@login_required
def view_maintenance_logs(customer_id):
    if not (current_user.is_admin or current_user.user_id == customer_id):
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
    chemranges = ChemicalRanges.query.all()
    if not (current_user.is_admin or visit.customer_id == current_user.user_id):
        flash("Access restricted.")
        return redirect(url_for('home'))
    
    return render_template('billing/maintenance_report.html', visit=visit, chemranges = chemranges)

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
