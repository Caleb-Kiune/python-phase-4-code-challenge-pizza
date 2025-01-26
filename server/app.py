#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, jsonify, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

class RestaurantsResource(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return jsonify([restaurant.to_dict() for restaurant in restaurants])

api.add_resource(RestaurantsResource, "/restaurants")

class RestaurantResource(Resource):
    def get(self, id):
        restaurant = db.session.get(Restaurant, id)
        if restaurant:
            restaurant_pizzas = [
                {
                    "id": rp.id,
                    "price": rp.price,
                    "pizza_id": rp.pizza_id,
                    "pizza": rp.pizza.to_dict()
                }
                for rp in restaurant.restaurant_pizzas
            ]
            response_data = {
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address,
                "restaurant_pizzas": restaurant_pizzas
            }
            return jsonify(response_data)
        else:
            return make_response(jsonify({"error": "Restaurant not found"}), 404)

    def delete(self, id):
        restaurant = db.session.get(Restaurant, id)
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return make_response("", 204)
        else:
            return make_response(jsonify({"error": "Restaurant not found"}), 404)

api.add_resource(RestaurantResource, "/restaurants/<int:id>")

class PizzasResource(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return jsonify([pizza.to_dict() for pizza in pizzas])

api.add_resource(PizzasResource, "/pizzas")

class RestaurantPizzasResource(Resource):
    def post(self):
        data = request.get_json()
        print("Received data:", data)  # Debugging: Print received data
        try:
            new_restaurant_pizza = RestaurantPizza(
                price=data.get("price"),
                restaurant_id=data.get("restaurant_id"),
                pizza_id=data.get("pizza_id")
            )
            db.session.add(new_restaurant_pizza)
            db.session.commit()
            response_data = new_restaurant_pizza.to_dict()
            print("Response data:", response_data)  # Debugging: Print response data
            return jsonify(response_data), 201
        except ValueError as e:
            print("Validation Error:", str(e))  # Debugging: Print validation error
            return make_response(jsonify({"errors": ["validation errors"]}), 400)
        except Exception as e:
            print("Unexpected Error:", str(e))  # Debugging: Print unexpected error
            return make_response(jsonify({"errors": [str(e)]}), 500)

api.add_resource(RestaurantPizzasResource, "/restaurant_pizzas")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
