from google.cloud import storage

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
