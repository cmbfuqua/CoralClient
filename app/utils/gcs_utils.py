from google.cloud import storage

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_image_to_gcs(user_folder, filename, file):
    """
    Uploads a file to Google Cloud Storage.
    """
    BUCKET_NAME = 'corals4cheapbuckets'
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob_path = f"{user_folder}/{filename}"
    blob = bucket.blob(blob_path)
    blob.upload_from_file(file, rewind=True)
    return blob.public_url

def delete_image_from_gcs(image_url):
    """
    Deletes the image from Google Cloud Storage given the image URL.
    """
    try:
        bucket_name = "corals4cheapbuckets"
        file_path = image_url.split(f"https://storage.googleapis.com/{bucket_name}/")[-1]
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_path)
        if blob.exists():
            blob.delete()
        print(f"Image {file_path} successfully deleted from Google Cloud Storage.")
    except Exception as e:
        print(f"Error deleting image from Google Cloud Storage: {e}")
