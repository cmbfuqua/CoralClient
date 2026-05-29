from flask import render_template
from . import main_bp
from ..models import ConsignmentProduct, Order

@main_bp.route('/')
def home():
    featured_products = (
        ConsignmentProduct.query
        .filter_by(featured=True)
        .filter(ConsignmentProduct.order_status != 'C')
        .all()
    )
    orders = Order.query.all()
    return render_template('home.html', featured_products=featured_products, orders=orders)

@main_bp.route('/about_us')
def about_us():
    return render_template('about_us.html')

@main_bp.route('/policy')
def policy():
    return render_template('policy.html')

@main_bp.route('/contact')
def contact():
    return render_template('contact.html')
