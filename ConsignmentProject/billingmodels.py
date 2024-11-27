from flask_sqlalchemy import SQLAlchemy
from DB import db,app
from datetime import datetime

class MaintenanceVisit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
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
    date_of_visit = db.Column(db.DateTime, default=datetime.now())

class Bill(db.Model):
    __tablename__ = 'Bill'
    id = db.Column(db.Integer, primary_key=True)
    visit_id = db.Column(db.Integer, db.ForeignKey('MaintenanceVisit.id'), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    is_paid = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    paid_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    line_items = db.relationship('BillLineItem', backref='bill', cascade="all, delete-orphan")

class BillLineItem(db.Model):
    __tablename__ = 'BillLineItem'
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('Bill.id'), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)

    @property
    def total_price(self):
        return self.quantity * self.unit_price