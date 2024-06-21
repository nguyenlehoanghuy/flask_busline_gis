import os
import psycopg2

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required
from models import User, BusStation, BusLine
from utils import validate_email_and_password, validate_user

load_dotenv()

# App
jwt_secret = os.getenv('JWT_SECRET', '$3cr3t!')
jwt_access_token_expires = os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 900)
app_host = os.getenv('APP_HOST', 'localhost')
app_port = os.getenv('APP_PORT', 5000)
app_debug = os.getenv('APP_DEBUG', 'true').lower() in ['true', '1']
# Database
db_host = os.getenv('DB_HOST', 'localhost')
db_port = os.getenv('DB_PORT', '5432')
db_dbname = os.getenv('DB_DATABASE', 'busline_gis')
db_user = os.getenv('DB_USERNAME', 'postgres')
db_password = os.getenv('DB_PASSWORD', '123456')

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['JWT_SECRET_KEY'] = jwt_secret
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(jwt_access_token_expires)

cors = CORS(app)
jwt = JWTManager(app)

conn = psycopg2.connect(dbname=db_dbname, user=db_user,
                        password=db_password, host='localhost', port=db_port)


@app.route("/")
@cross_origin()
def hello():
    return "Hello World!"

# Auth


@app.route("/auth/login", methods=["POST"])
@cross_origin()
def login():
    try:
        data = request.json
        if not data:
            return {
                "message": "Please provide email, password",
                "data": None,
                "error": "Bad request"
            }, 400
        # Validate input
        # is_validated = validate_email_and_password(
        #     data.get('email'), data.get('password'))
        # if is_validated is not True:
        #     return {
        #         "message": "Invalid data",
        #         "data": None,
        #         "error": is_validated}, 400
        token = User(conn).login(
            data["email"],
            data["password"]
        )
        if token:
            expires_in = int(jwt_access_token_expires)
            token["expires_in"] = expires_in
            return token
        return {
            "message": "Error fetching auth token!, invalid email or password",
            "data": None,
            "error": "Unauthorized"
        }, 401
    except Exception as e:
        return {
            "message": "Something went wrong!",
            "error": str(e),
            "data": None
        }, 500


@app.route("/auth/register", methods=["POST"])
@cross_origin()
def register():
    try:
        data = request.json
        if not data:
            return {
                "message": "Please provide email, password",
                "data": None,
                "error": "Bad request"
            }, 400
        # Validate input
        # is_validated = validate_email_and_password(
        #     data.get('email'), data.get('password'))
        # if is_validated is not True:
        #     return {
        #         "message": "Invalid data",
        #         "data": None,
        #         "error": is_validated}, 400
        token = User(conn).create_user(
            data["email"], data["name"], data["password"])
        if token:
            expires_in = int(jwt_access_token_expires)
            token["expires_in"] = expires_in
            return token
        return {
            "message": "User already exists",
            "data": None,
            "error": "Conflict"
        }, 409
    except Exception as e:
        return {
            "message": "Something went wrong!",
            "error": str(e),
            "data": None
        }, 500


@app.route("/auth/me", methods=["GET"])
@cross_origin()
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    user = User(conn).get_user_by_id(current_user_id)
    return jsonify({
        "message": "Successfully retrieved user profile",
        "data": user
    }), 200

# Users management


@app.route("/users", methods=["GET"])
@cross_origin()
@jwt_required()
def gat_all_users():
    try:
        user = User(conn).get_all_users()
        return jsonify({
            "message": "Successfully retrieved all users",
            "data": user
        }), 200
    except Exception as e:
        return {
            "message": "Something went wrong",
            "error": str(e),
            "data": None
        }, 500

# Bus stations management


@app.route("/bus_stations", methods=["GET"])
@cross_origin()
def get_all_bus_stations():
    try:
        bus_stations = BusStation(conn).get_all_bus_stations()
        return jsonify({
            "message": "Successfully retrieved bus stations",
            "data": bus_stations
        }), 200
    except Exception as e:
        return {
            "message": "Something went wrong",
            "error": str(e),
            "data": None
        }, 500


@app.route("/bus_stations/<bus_station_id>", methods=["GET"])
@cross_origin()
def get_bus_station_by_id(bus_station_id):
    try:
        bus_station = BusStation(conn).get_bus_station_by_id(bus_station_id)
        if not bus_station:
            return {
                "message": "Bus station not found",
                "data": None,
                "error": "Not Found"
            }, 404
        return jsonify({
            "message": "Successfully retrieved a bus station",
            "data": bus_station
        }), 200
    except Exception as e:
        return {
            "message": "Something went wrong",
            "error": str(e),
            "data": None
        }, 500


@app.route("/bus_stations", methods=["POST"])
@cross_origin()
@jwt_required()
def create_bus_station():
    try:
        data = request.json
        if not data:
            return {
                "message": "Invalid data",
                "data": None,
                "error": "Bad request"
            }, 400
        # Validate input
        # is_validated = validate_email_and_password(
        #     data.get('email'), data.get('password'))
        # if is_validated is not True:
        #     return {
        #         "message": "Invalid data",
        #         "data": None,
        #         "error": is_validated}, 400
        bus_station = BusStation(conn).create_bus_station(
            data["name"], data["long"], data["lat"], data["address"], data["id_ward"])
        return jsonify({
            "message": "Successfully created a bus station",
            "data": bus_station
        }), 201
    except Exception as e:
        return jsonify({
            "message": "Failed to create a bus station",
            "error": str(e),
            "data": None
        }), 500


@app.route("/bus_stations/<bus_station_id>", methods=["PUT"])
@cross_origin()
@jwt_required()
def update_bus_station(bus_station_id):
    try:
        bus_station = BusStation(conn).get_bus_station_by_id(bus_station_id)
        if not bus_station:
            return {
                "message": "Bus station not found",
                "data": None,
                "error": "Not found"
            }, 404
        data = request.json
        if not data:
            return {
                "message": "Invalid data",
                "data": None,
                "error": "Bad request"
            }, 400
        # Validate input
        # is_validated = validate_email_and_password(
        #     data.get('email'), data.get('password'))
        # if is_validated is not True:
        #     return {
        #         "message": "Invalid data",
        #         "data": None,
        #         "error": is_validated}, 400
        bus_station = BusStation(conn).update_bus_station(
            bus_station_id, data["name"], data["long"], data["lat"], data["address"], data["id_ward"])
        return jsonify({
            "message": "Successfully updated a bus station",
            "data": bus_station
        }), 201
    except Exception as e:
        return jsonify({
            "message": "failed to update a bus station",
            "error": str(e),
            "data": None
        }), 400


@app.route("/bus_stations/<bus_station_id>", methods=["DELETE"])
@cross_origin()
@jwt_required()
def delete_bus_station(bus_station_id):
    try:
        bus_station = BusStation(conn).get_bus_station_by_id(bus_station_id)
        if not bus_station:
            return {
                "message": "Bus station not found",
                "data": None,
                "error": "Not found"
            }, 404
        bus_station = BusStation(conn).delete_bus_station(bus_station_id)
        return jsonify({
            "message": "Successfully deleted a bus station",
            "data": None
        }), 204
    except Exception as e:
        return jsonify({
            "message": "failed to delete a bus station",
            "error": str(e),
            "data": None
        }), 400

# Bus lines management


@app.route("/bus_lines", methods=["GET"])
@cross_origin()
def get_all_bus_lines():
    try:
        bus_lines = BusLine(conn).get_all_bus_lines()
        return jsonify({
            "message": "Successfully retrieved bus lines",
            "data": bus_lines
        }), 200
    except Exception as e:
        return {
            "message": "Something went wrong",
            "error": str(e),
            "data": None
        }, 500


@app.route("/bus_lines/<bus_line_id>", methods=["GET"])
@cross_origin()
def get_bus_line_by_id(bus_line_id):
    try:
        bus_line = BusLine(conn).get_bus_line_by_id(bus_line_id)
        if not bus_line:
            return {
                "message": "bus line not found",
                "data": None,
                "error": "Not Found"
            }, 404
        return jsonify({
            "message": "Successfully retrieved a bus line",
            "data": bus_line
        }), 200
    except Exception as e:
        return {
            "message": "Something went wrong",
            "error": str(e),
            "data": None
        }, 500


@app.route("/bus_lines", methods=["POST"])
@cross_origin()
@jwt_required()
def create_bus_line():
    try:
        data = request.json
        if not data:
            return {
                "message": "Invalid data",
                "data": None,
                "error": "Bad request"
            }, 400
        # Validate input
        # is_validated = validate_email_and_password(
        #     data.get('email'), data.get('password'))
        # if is_validated is not True:
        #     return {
        #         "message": "Invalid data",
        #         "data": None,
        #         "error": is_validated}, 400
        bus_line = BusLine(conn).create_bus_line(
            data["name"], data["length"], data["price"], data["number_of_trips"], data["time_between_trips"], data["start_time_first"])
        return jsonify({
            "message": "Successfully created a bus line",
            "data": bus_line
        }), 201
    except Exception as e:
        return jsonify({
            "message": "Failed to create a bus line",
            "error": str(e),
            "data": None
        }), 500


@app.route("/bus_lines/<bus_line_id>", methods=["PUT"])
@cross_origin()
@jwt_required()
def update_bus_line(bus_line_id):
    try:
        bus_line = BusLine(conn).get_bus_line_by_id(bus_line_id)
        if not bus_line:
            return {
                "message": "bus line not found",
                "data": None,
                "error": "Not found"
            }, 404
        data = request.json
        if not data:
            return {
                "message": "Invalid data",
                "data": None,
                "error": "Bad request"
            }, 400
        # Validate input
        # is_validated = validate_email_and_password(
        #     data.get('email'), data.get('password'))
        # if is_validated is not True:
        #     return {
        #         "message": "Invalid data",
        #         "data": None,
        #         "error": is_validated}, 400
        bus_line = BusLine(conn).update_bus_line(
            bus_line_id, data["name"], data["length"], data["price"], data["number_of_trips"], data["time_between_trips"], data["start_time_first"])
        return jsonify({
            "message": "Successfully updated a bus line",
            "data": bus_line
        }), 201
    except Exception as e:
        return jsonify({
            "message": "failed to update a bus line",
            "error": str(e),
            "data": None
        }), 400


@app.route("/bus_lines/<bus_line_id>", methods=["DELETE"])
@cross_origin()
@jwt_required()
def delete_bus_line(bus_line_id):
    try:
        bus_line = BusLine(conn).get_bus_line_by_id(bus_line_id)
        if not bus_line:
            return {
                "message": "Bus station not found",
                "data": None,
                "error": "Not found"
            }, 404
        bus_line = BusLine(conn).delete_bus_line(bus_line_id)
        return jsonify({
            "message": "Successfully deleted a bus station",
            "data": None
        }), 204
    except Exception as e:
        return jsonify({
            "message": "failed to delete a bus station",
            "error": str(e),
            "data": None
        }), 400


@app.errorhandler(403)
def for_bidden(e):
    return jsonify({
        "message": "For bidden",
        "error": str(e),
        "data": None
    }), 403


@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "message": "Not found",
        "error": str(e),
        "data": None
    }), 404


if __name__ == "__main__":
    app.run(host=app_host, port=int(app_port), debug=app_debug)
