from flask import render_template
from flask_mail import Message
from billingroutes import *
from google.cloud import storage

from functools import wraps

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
    BUCKET_NAME = 'corals4cheapbuckets'

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

def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("You must be logged in to access this page.", "warning")
            return redirect(url_for('login'))
        if not current_user.is_admin:  # Directly check `is_admin` attribute
            flash("You do not have permission to access this page.", "danger")
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    return decorated_view

def delete_image_from_gcs(image_url):
    """
    Deletes the image from Google Cloud Storage given the image URL.
    
    Args:
        image_url (str): The URL of the image to be deleted.
    
    Returns:
        None
    """
    try:
        # Extract the file path from the image URL (assuming the image URL is a direct link)
        # Example: 'https://storage.googleapis.com/your-bucket-name/path/to/image.jpg'
        # Define the bucket name
        bucket_name = "corals4cheapbuckets"  # Replace with your actual bucket name
        file_path = image_url.split(f"https://storage.googleapis.com/{bucket_name}/")[-1]

        # Initialize the Google Cloud Storage client
        storage_client = storage.Client()


        # Get the bucket object
        bucket = storage_client.bucket(bucket_name)

        blob = bucket.blob(file_path)
        if blob.exists():
            blob.delete()

        print(f"Image {file_path} successfully deleted from Google Cloud Storage.")

    except Exception as e:
        print(f"Error deleting image from Google Cloud Storage: {e}")


