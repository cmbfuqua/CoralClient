from app import app, db
from models import *
from billingmodels import *

def setup_database():
    """
    This function creates the database and all the tables.
    """
    try:
        with app.app_context():
            db.create_all()
        print("Database and tables created successfully.")
    except Exception as e:
        print(f"An error occurred during database setup: {e}")

if __name__ == '__main__':
    setup_database()
