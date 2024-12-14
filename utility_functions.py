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
        html=render_template('emails/order_notification_email.html', product=product, order_id=order_number)
    )
    mail.send(msg)

def send_dropoff_notification(buyer, product, seller,order):
    msg = Message("Coral Dropoff Notification", recipients=[buyer.email])
    msg.html = render_template('emails/dropoff_notification.html', buyer=buyer, product=product, seller=seller,order=order)
    mail.send(msg)

def send_pickup_notification(buyer, product, seller,order):
    msg = Message("Coral Pickup Complete", recipients=[seller.email])
    msg.html = render_template('emails/pickup_notification.html', buyer=buyer, seller=seller, product=product,order=order)
    mail.send(msg)

def send_cancellation_notification(buyer, product, seller,order):
    msg = Message("Order Canceled", recipients=[buyer.email,seller.email])
    msg.html = render_template('emails/cancellation_notification.html', seller=seller, product=product, buyer=buyer,order=order)
    mail.send(msg)

def upload_image_to_gcs(user_folder, filename, file):
    """
    Uploads a file to Google Cloud Storage.
    Args:
        user_folder (str): The folder path inside the GCS bucket.
        filename (str): The name of the file to upload.
        file (BytesIO): The in-memory file object.
    Returns:
        str: The GCS public URL or path to the uploaded file.
    """
    # Define your GCS bucket name
    BUCKET_NAME = 'corals4cheapbucket'

    # Initialize the GCS client
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)

    # Define the blob path in GCS (user folder structure)
    blob_path = f"{user_folder}/{filename}"

    # Create a new blob and upload the file to GCS
    blob = bucket.blob(blob_path)
    blob.upload_from_file(file, rewind=True)  # Use the file-like object

    # Return the public URL of the uploaded file
    return blob.public_url




