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
    #MAIL_SERVER = 'smtp.gmail.com'
    #MAIL_PORT = 587
    #MAIL_USE_TLS = True
    #MAIL_USE_SSL = False
    #MAIL_USERNAME = 'your_gmail_username@gmail.com'
    #MAIL_PASSWORD = 'your_gmail_password'
    #MAIL_DEFAULT_SENDER = 'your_gmail_username@gmail.com'



