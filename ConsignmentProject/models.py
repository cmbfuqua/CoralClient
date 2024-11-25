from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from DB import db,app

# User model
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), nullable=False)
    
    role = db.relationship('Role', backref='users')

    @property
    def is_admin(self):
        return self.role_id == 3
    
    @property
    def is_seller(self):
        return self.role_id == 2
    
    def get_id(self):
        return str(self.user_id)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Role model
class Role(db.Model):
    __tablename__ = 'roles'
    role_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    #users = db.relationship('Users',backref='role')

# Permissions model
class Permission(db.Model):
    __tablename__ = 'permissions'
    permission_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

# RolePermissions association table
role_permissions = db.Table('role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.role_id')),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.permission_id'))
)

# Item Type model
class ItemType(db.Model):
    __tablename__ = 'item_types'
    item_type_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

# Item Subtype model
class ItemSubtype(db.Model):
    __tablename__ = 'item_subtypes'
    item_subtype_id = db.Column(db.Integer, primary_key=True)
    item_type_id = db.Column(db.Integer, db.ForeignKey('item_types.item_type_id'))
    name = db.Column(db.String(50), nullable=False)

# Consignment Product model
class ConsignmentProduct(db.Model):
    __tablename__ = 'consignment_products'
    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    image_url = db.Column(db.String(255))
    featured = db.Column(db.Boolean,nullable=False,default=0)
    item_type_id = db.Column(db.Integer, db.ForeignKey('item_types.item_type_id'))
    item_subtype_id = db.Column(db.Integer, db.ForeignKey('item_subtypes.item_subtype_id'))
    seller_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

# Order model
class Order(db.Model):
    __tablename__ = 'orders'
    order_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('consignment_products.product_id'))
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    seller_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    order_date = db.Column(db.DateTime, default=db.func.current_timestamp())
