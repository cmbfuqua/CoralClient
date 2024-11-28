from flask_sqlalchemy import SQLAlchemy
from DB import db,app
from datetime import datetime
#from models import User

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
    date_of_visit = db.Column(db.DateTime, default=datetime.now())

    bill = db.relationship('Bill', backref='maintenance_visit', uselist=False)
    customer = db.relationship('User',backref='maintenance_visit',uselist=False)

class Bill(db.Model):
    __tablename__ = 'Bill'
    BillID = db.Column(db.Integer, primary_key=True)
    visitID = db.Column(db.Integer, db.ForeignKey('maintenance_visits.visit_id'), nullable=False)
    TotalAmount = db.Column(db.Float, nullable=False, default=0.00)
    IsPaid = db.Column(db.Boolean, default=False)
    CreatedAt = db.Column(db.Date, default=datetime.now())
    PaidAt = db.Column(db.Date, nullable=True)
    Notes = db.Column(db.Text, nullable=True)

    line_items = db.relationship('BillLineItem', backref='bill', cascade="all, delete-orphan")
    visit = db.relationship('MaintenanceVisit',backref='bills')

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