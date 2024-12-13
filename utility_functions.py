from flask import render_template
from flask_mail import Message
from werkzeug.utils import secure_filename
from billingroutes import *
from waitress import serve
from google.cloud import storage


from DB import app

mail = Mail(app)


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
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
    msg = Message("Coral Pickup Complete", recipients=[seller.email])
    msg.html = render_template('pickup_notification.html', buyer=buyer, seller=seller, product=product,order=order)
    mail.send(msg)

def send_cancellation_notification(buyer, product, seller,order):
    msg = Message("Order Canceled", recipients=[buyer.email,seller.email])
    msg.html = render_template('cancellation_notification.html', seller=seller, product=product, buyer=buyer,order=order)
    mail.send(msg)

def upload_image_to_gcs(user_folder, file):
    """
    Uploads a file to Google Cloud Storage.
    :param user_folder: The folder path inside the GCS bucket.
    :param file: The Werkzeug FileStorage object.
    :return: The GCS path or URL to store in your DB (without the signed URL).
    """
    if file:
        # Secure the filename to prevent malicious file names
        filename = secure_filename(file.filename)

        # Define your GCS bucket name
        BUCKET_NAME = 'corals4cheapbucket'

        # Initialize the GCS client
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)

        # Define the blob path in GCS (user folder structure)
        blob_path = f"{user_folder}/{filename}"

        # Create a new blob and upload the image file to GCS
        blob = bucket.blob(blob_path)
        
        # Use `file.stream` to get the file-like object from FileStorage
        blob.upload_from_file(file.stream)

        # Return the GCS path for later use (without generating signed URL)
        return blob.public_url # Return the path, not the public URL yet

    else:
        return None



from google.cloud import storage
from datetime import timedelta

def generate_signed_url(bucket_name, blob_name, expiration_time=3600):
    """Generate a signed URL for accessing a GCS object."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    # Generate signed URL valid for `expiration_time` seconds
    url = blob.generate_signed_url(expiration=timedelta(seconds=expiration_time))
    return url


