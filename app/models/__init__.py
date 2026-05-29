from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from ..extensions import db

# association table
role_permissions = db.Table('role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.role_id')),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.permission_id'))
)

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
    is_maintenance = db.Column(db.Boolean,nullable=False,default=0)
    in_store_credit = db.Column(db.Float)
    role = db.relationship('Role', backref='users')
    PasswordReset = db.Column(db.Boolean,default = 0)
    notes = db.Column(db.String(1500),default='')

    @property
    def is_admin(self):
        return self.role_id == 3
    
    @property
    def is_seller(self):
        return self.role_id in [2,3]
    
    @property
    def maintenance_folder_path(self):
        return (str(self.first_name).strip() + str(self.last_name).strip() + str(self.user_id)).replace(" ", "")
    
    def get_id(self):
        return str(self.user_id)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def __repr__(self):
        return f"<User {self.username} (ID: {self.user_id})>"

# Role model
class Role(db.Model):
    __tablename__ = 'roles'
    role_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    
    def __repr__(self):
        return f"<Role {self.name}>"

# Permissions model
class Permission(db.Model):
    __tablename__ = 'permissions'
    permission_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

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
    order_status = db.Column(db.String(5),nullable=False)

    item_type = db.relationship('ItemType', backref='consignment_products', lazy=True)
    item_subtype = db.relationship('ItemSubtype', backref='consignment_products', lazy=True)
    seller = db.relationship('User',backref = 'consignment_products',lazy=True)
    
    def __repr__(self):
        return f"<ConsignmentProduct {self.name} - ${self.price}>"

# Order model
class Order(db.Model):
    __tablename__ = 'orders'
    order_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('consignment_products.product_id'))
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    seller_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    order_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    product_dropoff = db.Column(db.Date)
    product_pickup = db.Column(db.Date)
    payment_status = db.Column(db.String(50))
    order_status = db.Column(db.String(5),nullable=False)

    product = db.relationship('ConsignmentProduct', backref='orders', lazy=True)
    buyer = db.relationship('User', foreign_keys=[buyer_id], backref='buyer_orders', lazy=True)
    seller = db.relationship('User', foreign_keys=[seller_id], backref='seller_orders', lazy=True)
    
    def __repr__(self):
        return f"<Order {self.order_id} - Status: {self.order_status}>"

class MaintenanceVisit(db.Model):
    __tablename__ = 'maintenance_visits'
    visit_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    before_picture = db.Column(db.String(255))
    ammonia = db.Column(db.Float)
    nitrite = db.Column(db.Float)
    nitrate = db.Column(db.Float)
    ph = db.Column(db.Float)
    phosphates = db.Column(db.Float)
    calcium = db.Column(db.Float)
    magnesium = db.Column(db.Float)
    alkalinity = db.Column(db.Float)
    notes = db.Column(db.Text)
    recommendations = db.Column(db.Text)
    after_picture = db.Column(db.String(255))
    date_of_visit = db.Column(db.DateTime, default=datetime.now)

    bill = db.relationship('Bill', back_populates='visit', uselist=False)
    customer = db.relationship('User', backref='maintenance_visits', uselist=False)
    
    def __repr__(self):
        return f"<MaintenanceVisit {self.visit_id} for Customer {self.customer_id}>"

class Bill(db.Model):
    __tablename__ = 'Bill'
    BillID = db.Column(db.Integer, primary_key=True)
    visitID = db.Column(db.Integer, db.ForeignKey('maintenance_visits.visit_id'), nullable=False)
    TotalAmount = db.Column(db.Float, nullable=False, default=0.00)
    SubTotal = db.Column(db.Float,nullable=False)
    Tax = db.Column(db.Float,nullable=False)
    IsPaid = db.Column(db.Boolean, default=False)
    CreatedAt = db.Column(db.Date, default=lambda: datetime.now().date())
    PaidAt = db.Column(db.Date, nullable=True)
    Notes = db.Column(db.Text, nullable=True)

    line_items = db.relationship('BillLineItem', backref='bill', cascade="all, delete-orphan")
    visit = db.relationship('MaintenanceVisit', back_populates='bill')
    
    def __repr__(self):
        return f"<Bill {self.BillID} - Paid: {self.IsPaid}>"

class BillLineItem(db.Model):
    __tablename__ = 'BillLineItem'
    LineItemID = db.Column(db.Integer, primary_key=True)
    BillID = db.Column(db.Integer, db.ForeignKey('Bill.BillID'), nullable=False)
    Description = db.Column(db.String(255), nullable=False)
    Quantity = db.Column(db.Integer, nullable=False, default=1)
    UnitPrice = db.Column(db.Numeric(10, 2), nullable=False)

    @property
    def TotalPrice(self):
        return self.Quantity * self.UnitPrice
        
    def __repr__(self):
        return f"<BillLineItem {self.Description} (x{self.Quantity})>"
    
class ChemicalRanges(db.Model):
    __tablename__ = 'ChemicalRanges'
    ChemID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ChemName = db.Column(db.String(100), nullable=False)
    MinValues = db.Column(db.Float, nullable=False)
    MaxValues = db.Column(db.Float, nullable=False)
    Optimal = db.Column(db.Float, nullable=False)
