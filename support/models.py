from flask import Flask
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime, date, timedelta
import pytz

db = SQLAlchemy()

shopping = db.Table('shopping',
                db.Column('product_id', db.Integer, db.ForeignKey('product.id')),
                db.Column('cart_id', db.Integer, db.ForeignKey('cart.id'))
                )

tagging = db.Table('tagging',
                db.Column('product_id', db.Integer, db.ForeignKey('product.id')),
                db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
                )

sharing = db.Table('sharing',
                db.Column('details_id', db.Integer, db.ForeignKey('details.id')),
                db.Column('ingredient_id', db.Integer, db.ForeignKey('ingredient.id'))
                )

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    unique = db.Column(db.String(50), nullable=False)

    cart = db.relationship('Cart', backref='owner', uselist=False)
    picks = db.relationship('Pick', backref='user')
    orders = db.relationship('Order', backref='buyer')

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total_cost = db.Column(db.Float, default=0)
    discount = db.Column(db.Float, default=0)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def size(self):
        products = [product for product in self.contents]
        return len(products)

    def bill(self, count_dict):
        self.total_cost = 0
        db.session.commit()
        products = [product for product in self.contents]
        if products:
            for product in products:
                self.total_cost += product.price * count_dict[product.id]
            db.session.commit()

    def reset(self):
        if self.total_cost < 0:
            self.total_cost = 0
            db.session.commit()

    def discounted(self):
        return self.total_cost * (1 - self.discount)

    def get_price(self):
        return "${:,.2f}".format(self.total_cost)

    def __repr__(self):
        return '<Cart %r>' % self.id

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=1)
    is_stocked = db.Column(db.Boolean, default=True)
    is_discounted = db.Column(db.Boolean, default=False)

    details = db.relationship('Details', backref='product', uselist=False)
    picks = db.relationship('Pick', backref='product')
    carts = db.relationship('Cart', secondary=shopping, backref=db.backref('contents', lazy='dynamic'))

    def get_price(self):
        return "${:,.2f}".format(self.price)

    def restock(self, count):
        self.stock += count
        db.session.commit()

    def sold(self, count):
        self.stock -= count
        db.session.commit()

    def __repr__(self):
        return '<Product %r>' % self.id

class Details(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_featured = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text, default='This is a great product.')
    instructions = db.Column(db.Text, default='Instructions to this product here.')

    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))

    def shorten(self):
        shorten = ''
        if len(self.description) > 137:
            for i in range(137):
                shorten += self.description[i]
            shorten += "..."
        else:
            shorten = self.description
        return shorten

    def __repr__(self):
        return '<Details %r>' % self.id

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)

    categories = db.relationship('Product', secondary=tagging, backref=db.backref('tags', lazy='dynamic'))

    def __repr__(self):
        return '<Tag %r>' % self.id

class Pick(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, nullable=False)

    shopper_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))

    def __repr__(self):
        return '<Pick %r>' % self.id

class Code(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    discount = db.Column(db.Float, default=0)

    def __repr__(self):
        return '<Code %r>' % self.id

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gross = db.Column(db.Float, nullable=False)
    fee = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    txn_id = db.Column(db.Integer, nullable=False)
    date_completed = db.Column(db.DateTime, default=datetime.now(tz=pytz.UTC))

    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Order %r>' % self.id

class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    source = db.Column(db.String(50), nullable=False)

    details = db.relationship('Details', secondary=sharing, backref=db.backref('ingredients', lazy='dynamic'))

    def __repr__(self):
        return '<Ingredient %r>' % self.id
