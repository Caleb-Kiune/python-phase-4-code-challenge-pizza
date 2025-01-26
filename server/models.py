from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)

class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # Add relationship
    restaurant_pizzas = relationship('RestaurantPizza', backref='restaurant_ref', cascade="all, delete-orphan")
    pizzas = association_proxy('restaurant_pizzas', 'pizza')

    # Add serialization rules
    serialize_rules = ('-restaurant_pizzas.restaurant_ref',)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'pizzas': [pizza.to_dict() for pizza in self.pizzas]
        }

    def __repr__(self):
        return f"<Restaurant {self.name}>"

class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # Add relationship
    restaurant_pizzas = relationship('RestaurantPizza', backref='pizza_ref', cascade="all, delete-orphan")
    restaurants = association_proxy('restaurant_pizzas', 'restaurant')

    # Add serialization rules
    serialize_rules = ('-restaurant_pizzas.pizza_ref',)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'ingredients': self.ingredients
        }

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"

class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    restaurant_id = db.Column(db.Integer, ForeignKey('restaurants.id'))
    pizza_id = db.Column(db.Integer, ForeignKey('pizzas.id'))

    # Add relationships
    restaurant = relationship('Restaurant', backref='restaurant_pizza_links', overlaps="restaurant_pizzas,restaurant_ref")
    pizza = relationship('Pizza', backref='pizza_pizza_links', overlaps="restaurant_pizzas,pizza_ref")

    # Add serialization rules
    serialize_rules = ('-restaurant.restaurant_pizza_links', '-pizza.pizza_pizza_links')

    @validates('price')
    def validate_price(self, key, price):
        if not 1 <= price <= 30:
            raise ValueError('Price must be between 1 and 30')
        return price

    def to_dict(self):
        return {
            'id': self.id,
            'price': self.price,
            'restaurant_id': self.restaurant_id,
            'pizza_id': self.pizza_id,
            'restaurant': self.restaurant.to_dict() if self.restaurant else None,  # Check if restaurant is None
            'pizza': self.pizza.to_dict() if self.pizza else None  # Check if pizza is None
        }

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"