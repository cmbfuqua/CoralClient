import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Pointing to SQL Server
    SQLALCHEMY_DATABASE_URI = (
        "mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver}"
    ).format(
        username="CoralClientSellerApp",  # Replace with your SQL Server username
        password="A7mX9zQpL2vRw3Y",  # Replace with your SQL Server password
        server="BEN_BLUE",         # Replace with your server name
        database="CoralClientSeller",  # Replace with your database name
        driver="ODBC Driver 17 for SQL Server"  # Ensure this driver is installed
    )
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static/uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'Corals4CheapAutomated@gmail.com'
    MAIL_PASSWORD = 'mabg kcyn vhnq joiq'
    MAIL_DEFAULT_SENDER = 'Corals4CheapAutomated@gmail.com'



