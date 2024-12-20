import os
from urllib.parse import quote
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Pointing to SQL Server
    prod = (
        "mysql+pymysql://{username}:{password}@/{database}?unix_socket=/cloudsql/{instance_connection_name}"
        ).format(
            username="CoralClientSellerApp", 
            password=quote("Corals4Ch3ap?"), 
            database="CoralClientSeller", 
            instance_connection_name="corals4cheapprod:us-west3:corals4cheapdb"
        )
    
    SQLALCHEMY_DATABASE_URI = prod

    GOOGLE_APPLICATION_CREDENTIALS = r"C:\Users\benja\Desktop\corals4cheap-65a82a68dbed.json"

    UPLOAD_FOLDER = '/data'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'Corals4CheapAutomated@gmail.com'
    MAIL_PASSWORD = 'mabg kcyn vhnq joiq'
    MAIL_DEFAULT_SENDER = 'Corals4CheapAutomated@gmail.com'



