from flask import current_app, render_template, flash, redirect, url_for
from flask_login import current_user
from flask_mail import Message
from functools import wraps
from ..extensions import mail

def send_order_notification(seller_email, product, order_number, buyer_first_name, buyer_last_name):
    """Sends an order creation notification."""
    msg = Message(
        subject="New Order Created",
        recipients=[seller_email],
        html=render_template('emails/order_notification_email.html', product=product, order_id=order_number)
    )
    mail.send(msg)

def send_dropoff_notification(buyer, product, seller, order):
    """Sends a drop-off notification."""
    msg = Message("Coral Dropoff Notification", recipients=[buyer.email])
    msg.html = render_template('emails/dropoff_notification.html', buyer=buyer, product=product, seller=seller, order=order)
    mail.send(msg)

def send_pickup_notification(buyer, product, seller, order):
    """Sends a pickup notification."""
    msg = Message("Coral Pickup Complete", recipients=[seller.email])
    msg.html = render_template('emails/pickup_notification.html', buyer=buyer, seller=seller, product=product, order=order)
    mail.send(msg)

def send_cancellation_notification(buyer, product, seller, order):
    """Sends an order cancellation notification."""
    msg = Message("Order Canceled", recipients=[buyer.email, seller.email])
    msg.html = render_template('emails/cancellation_notification.html', seller=seller, product=product, buyer=buyer, order=order)
    mail.send(msg)

def admin_required(func):
    """Decorator to require admin privileges for a route."""
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("You must be logged in to access this page.", "warning")
            return redirect(url_for('auth.login'))
        if not current_user.is_admin:
            flash("You do not have permission to access this page.", "danger")
            return redirect(url_for('main.home'))
        return func(*args, **kwargs)
    return decorated_view
