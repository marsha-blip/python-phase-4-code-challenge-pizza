#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
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


class RestaurantList(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return make_response([restaurant.to_dict(only=('id', 'name', 'address')) for restaurant in restaurants], 200)


api.add_resource(RestaurantList, "/restaurants")


class RestaurantByID(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return make_response({"error": "Restaurant not found"}, 404)
        return make_response(restaurant.to_dict(), 200)

    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return make_response({"error": "Restaurant not found"}, 404)
        db.session.delete(restaurant)
        db.session.commit()
        return make_response("", 204)


api.add_resource(RestaurantByID, "/restaurants/<int:id>")


class PizzaList(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return make_response([pizza.to_dict(only=('id', 'name', 'ingredients')) for pizza in pizzas], 200)


api.add_resource(PizzaList, "/pizzas")


class RestaurantPizzaList(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_restaurant_pizza = RestaurantPizza(
                price=data["price"],
                pizza_id=data["pizza_id"],
                restaurant_id=data["restaurant_id"],
            )
            db.session.add(new_restaurant_pizza)
            db.session.commit()
            return make_response(new_restaurant_pizza.to_dict(), 201)
        except ValueError as e:
            return make_response({"errors": ["validation errors"]}, 400)


api.add_resource(RestaurantPizzaList, "/restaurant_pizzas")

if __name__ == "__main__":
    app.run(port=5555, debug=True)





