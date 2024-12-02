import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Pointing to SQL Server
    dev = ("mysql+pymysql://{username}:{password}@localhost:3306/{database}"
           ).format(username="CoralClientSellerApp",
                    password="A7mX9zQpL2vRw3Y",
                    database="CoralClientSeller")
    prod = (
            "mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
            ).format(
                    username="root",  # Replace with your Railway database username
                    password="frbXYJpvZFeTxKYQCFSmxeFGgDasxAJz",  # Replace with your Railway database password
                    host="mysql.railway.internal",        # Host URL for Railway MySQL
                    port="3306",                          # MySQL default port
                    database="railway"         # The name of your database
            )
    
    SQLALCHEMY_DATABASE_URI = prod

    UPLOAD_FOLDER = os.path.join(os.getcwd(), '/data/uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'Corals4CheapAutomated@gmail.com'
    MAIL_PASSWORD = 'mabg kcyn vhnq joiq'
    MAIL_DEFAULT_SENDER = 'Corals4CheapAutomated@gmail.com'



