import os

# 1. Set the environment variable so DB.py loads DevConfig (SQLite)
os.environ['FLASK_ENV'] = 'development'

# 2. Import setup components (Must happen after setting FLASK_ENV)
from setup_db import setup_database
from app import app, bcrypt
from DB import db
from models import Role, ItemType, ItemSubtype, User, ConsignmentProduct
from datetime import date

def seed_data():
    """Seeds initial required data if the database is empty."""
    with app.app_context():
        # Check if roles exist; if not, we assume it's a fresh database
        if not Role.query.first():
            print("Seeding initial Roles and Item Types...")
            
            # Add default roles
            db.session.add_all([
                Role(role_id=1, name='user'),
                Role(role_id=2, name='seller'),
                Role(role_id=3, name='admin')
            ])
            
            # Add default item types
            db.session.add_all([
                ItemType(item_type_id=1, name='Coral'),
                ItemType(item_type_id=2, name='Fish'),
                ItemType(item_type_id=3, name='Equipment')
            ])
            
            # Add default item subtypes
            db.session.add_all([
                ItemSubtype(item_subtype_id=1, item_type_id=1, name='LPS'),
                ItemSubtype(item_subtype_id=2, item_type_id=1, name='SPS'),
                ItemSubtype(item_subtype_id=3, item_type_id=2, name='Clownfish'),
                ItemSubtype(item_subtype_id=4, item_type_id=2, name='Tang'),
                ItemSubtype(item_subtype_id=5, item_type_id=3, name='Lighting'),
                ItemSubtype(item_subtype_id=6, item_type_id=3, name='Pumps')
            ])
            
            # Add a default admin user
            admin_password = bcrypt.generate_password_hash("admin123").decode('utf-8')
            admin_user = User(
                username="admin", email="admin@test.com", password_hash=admin_password,
                first_name="Admin", last_name="User", dob=date(1990, 1, 1),
                phone_number="1234567890", role_id=3, in_store_credit=0.0
            )
            db.session.add(admin_user)
            
            # Add a default seller user
            seller_password = bcrypt.generate_password_hash("seller123").decode('utf-8')
            seller_user = User(
                username="seller", email="seller@test.com", password_hash=seller_password,
                first_name="Store", last_name="Seller", dob=date(1990, 1, 1),
                phone_number="0987654321", role_id=2, in_store_credit=0.0
            )
            db.session.add(seller_user)
            db.session.commit()
            
            print("Seeding dummy products...")
            
            # Add dummy products with realistic stock images
            products = [
                ConsignmentProduct(
                    name="Neon Green Hammer Coral", description="Beautiful glowing hammer coral.",
                    price=49.99, image_url="https://images.unsplash.com/photo-1546026423-cc46426ba658?auto=format&fit=crop&q=80&w=400&h=300",
                    featured=True, item_type_id=1, item_subtype_id=1, seller_id=seller_user.user_id, order_status='None'
                ),
                ConsignmentProduct(
                    name="Ocellaris Clownfish Pair", description="Bonded pair of healthy clownfish.",
                    price=75.00, image_url="https://images.unsplash.com/photo-1524704654690-b56c05c78a00?auto=format&fit=crop&q=80&w=400&h=300",
                    featured=True, item_type_id=2, item_subtype_id=3, seller_id=seller_user.user_id, order_status='None'
                ),
                ConsignmentProduct(
                    name="Reef LED Light 165W", description="Full spectrum LED lighting for coral growth.",
                    price=199.99, image_url="https://images.unsplash.com/photo-1583337130417-3346a1be7dee?auto=format&fit=crop&q=80&w=400&h=300",
                    featured=True, item_type_id=3, item_subtype_id=5, seller_id=seller_user.user_id, order_status='None'
                ),
                ConsignmentProduct(
                    name="Purple Tang", description="Vibrant and active algae eater.",
                    price=120.00, image_url="https://images.unsplash.com/photo-1522069169874-c58ec4b76be5?auto=format&fit=crop&q=80&w=400&h=300",
                    featured=True, item_type_id=2, item_subtype_id=4, seller_id=seller_user.user_id, order_status='None'
                )
            ]
            db.session.add_all(products)
            db.session.commit()
            
            print("\n*** SUCCESS: Database seeded with users and simulated products! ***")
            print("You can log in at http://127.0.0.1:8080 with:")
            print("Admin -> Email: admin@test.com | Password: admin123")
            print("Seller -> Email: seller@test.com | Password: seller123\n")

if __name__ == '__main__':
    setup_database()
    seed_data()
    print("Starting Flask development server...")
    app.run(host='127.0.0.1', port=8080, debug=True)