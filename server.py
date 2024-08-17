import os
import psycopg2

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required
from models import BusStation, BusLine, District, StationLine, User, Ward
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

# Districts management


@app.route("/districts", methods=["GET"])
@cross_origin()
def get_all_districts():
    try:
        districts = District(conn).get_all_districts()
        return jsonify({
            "message": "Successfully retrieved districts",
            "data": districts
        }), 200
    except Exception as e:
        return {
            "message": "Something went wrong",
            "error": str(e),
            "data": None
        }, 500


@app.route("/districts/<district_id>", methods=["GET"])
@cross_origin()
def get_district_by_id(district_id):
    try:
        district = District(conn).get_district_by_id(district_id)
        if not district:
            return {
                "message": "district not found",
                "data": None,
                "error": "Not Found"
            }, 404
        return jsonify({
            "message": "Successfully retrieved a district",
            "data": district
        }), 200
    except Exception as e:
        return {
            "message": "Something went wrong",
            "error": str(e),
            "data": None
        }, 500


@app.route("/districts", methods=["POST"])
@cross_origin()
@jwt_required()
def create_district():
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
        district = District(conn).create_district(data["id"], data["name"])
        return jsonify({
            "message": "Successfully created a district",
            "data": district
        }), 201
    except Exception as e:
        return jsonify({
            "message": "Failed to create a district",
            "error": str(e),
            "data": None
        }), 500


@app.route("/districts/<district_id>", methods=["PUT"])
@cross_origin()
@jwt_required()
def update_district(district_id):
    try:
        district = District(conn).get_district_by_id(district_id)
        if not district:
            return {
                "message": "district not found",
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
        district = District(conn).update_district(district_id, data["name"])
        return jsonify({
            "message": "Successfully updated a district",
            "data": district
        }), 201
    except Exception as e:
        return jsonify({
            "message": "failed to update a district",
            "error": str(e),
            "data": None
        }), 400


@app.route("/districts/<district_id>", methods=["DELETE"])
@cross_origin()
@jwt_required()
def delete_district(district_id):
    try:
        district = District(conn).get_district_by_id(district_id)
        if not district:
            return {
                "message": "Bus station not found",
                "data": None,
                "error": "Not found"
            }, 404
        district = District(conn).delete_district(district_id)
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

# Wards management


@app.route("/wards", methods=["GET"])
@cross_origin()
def get_all_wards():
    try:
        wards = Ward(conn).get_all_wards()
        return jsonify({
            "message": "Successfully retrieved wards",
            "data": wards
        }), 200
    except Exception as e:
        return {
            "message": "Something went wrong",
            "error": str(e),
            "data": None
        }, 500


@app.route("/wards/<ward_id>", methods=["GET"])
@cross_origin()
def get_ward_by_id(ward_id):
    try:
        id_district = ward_id[:4]
        id_ward = ward_id[-2:]
        ward = Ward(conn).get_ward_by_id(id_ward, id_district)
        if not ward:
            return {
                "message": "ward not found",
                "data": None,
                "error": "Not Found"
            }, 404
        return jsonify({
            "message": "Successfully retrieved a ward",
            "data": ward
        }), 200
    except Exception as e:
        return {
            "message": "Something went wrong",
            "error": str(e),
            "data": None
        }, 500


@app.route("/wards", methods=["POST"])
@cross_origin()
@jwt_required()
def create_ward():
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
        ward = Ward(conn).create_ward(
            data["id_ward"], data["id_district"], data["name"])
        return jsonify({
            "message": "Successfully created a ward",
            "data": ward
        }), 201
    except Exception as e:
        return jsonify({
            "message": "Failed to create a ward",
            "error": str(e),
            "data": None
        }), 500


@app.route("/wards/<ward_id>", methods=["PUT"])
@cross_origin()
@jwt_required()
def update_ward(ward_id):
    try:
        id_district = ward_id[:4]
        id_ward = ward_id[-2:]
        ward = Ward(conn).get_ward_by_id(id_ward, id_district)
        if not ward:
            return {
                "message": "ward not found",
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
        ward = ward(conn).update_ward(
            ward_id, data["name"], data["id_district"])
        return jsonify({
            "message": "Successfully updated a ward",
            "data": ward
        }), 201
    except Exception as e:
        return jsonify({
            "message": "failed to update a ward",
            "error": str(e),
            "data": None
        }), 400


@app.route("/wards/<ward_id>", methods=["DELETE"])
@cross_origin()
@jwt_required()
def delete_ward(ward_id):
    try:
        id_district = ward_id[:4]
        id_ward = ward_id[-2:]
        ward = Ward(conn).get_ward_by_id(id_ward, id_district)
        if not ward:
            return {
                "message": "Bus station not found",
                "data": None,
                "error": "Not found"
            }, 404
        ward = Ward(conn).delete_ward(ward_id)
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

# Station line management


@app.route("/bus_stations/<bus_station_id>/bus_lines", methods=["GET"])
@cross_origin()
def get_all_bus_lines_by_id_bus_station(bus_station_id):
    try:
        station_lines = StationLine(
            conn).get_all_bus_lines_by_id_bus_station(bus_station_id)
        return jsonify({
            "message": "Successfully retrieved all bus lines",
            "data": station_lines
        }), 200
    except Exception as e:
        return {
            "message": "Something went wrong",
            "error": str(e),
            "data": None
        }, 500


@app.route("/bus_lines/<bus_line_id>/bus_stations", methods=["GET"])
@cross_origin()
def get_all_bus_stations_by_id_bus_line(bus_line_id):
    try:
        station_lines = StationLine(
            conn).get_all_bus_stations_by_id_bus_line(bus_line_id)
        return jsonify({
            "message": "Successfully retrieved all bus stations",
            "data": station_lines
        }), 200
    except Exception as e:
        return {
            "message": "Something went wrong",
            "error": str(e),
            "data": None
        }, 500


@app.route("/bus_lines/<bus_line_id>/schedules", methods=["GET"])
@cross_origin()
def get_all_schedules_by_id_bus_line(bus_line_id):
    try:
        station_lines = StationLine(
            conn).get_all_schedules_by_id_bus_line(bus_line_id)
        return jsonify({
            "message": "Successfully retrieved all schedules",
            "data": station_lines
        }), 200
    except Exception as e:
        return {
            "message": "Something went wrong",
            "error": str(e),
            "data": None
        }, 500


@app.route("/bus_lines/<bus_line_id>/bus_stations/<bus_station_id>", methods=["GET"])
@cross_origin()
def get_station_line_by_id(bus_station_id, bus_line_id):
    try:
        station_line = StationLine(conn).get_station_line_by_id(
            bus_station_id, bus_line_id)
        return jsonify({
            "message": "Successfully created a station line",
            "data": station_line
        }), 201
    except Exception as e:
        return jsonify({
            "message": "Failed to create a station line",
            "error": str(e),
            "data": None
        }), 500


@app.route("/bus_lines/<bus_line_id>/bus_stations/<bus_station_id>", methods=["POST"])
@cross_origin()
@jwt_required()
def create_station_line(bus_station_id, bus_line_id):
    try:
        bus_line = BusLine(conn).get_bus_line_by_id(bus_line_id)
        if not bus_line:
            return {
                "message": "Bus line not found",
                "data": None,
                "error": "Not found"
            }, 404
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
        station_line = StationLine(conn).create_station_line(
            bus_station_id, bus_line_id, data["seq"], data["start_time_first"], data["distance"])
        return jsonify({
            "message": "Successfully created a station line",
            "data": station_line
        }), 201
    except Exception as e:
        return jsonify({
            "message": "Failed to create a station line",
            "error": str(e),
            "data": None
        }), 500


@app.route("/bus_lines/<bus_line_id>/bus_stations/<bus_station_id>", methods=["PUT"])
@cross_origin()
@jwt_required()
def update_station_line(bus_station_id, bus_line_id):
    try:
        bus_line = BusLine(conn).get_bus_line_by_id(bus_line_id)
        if not bus_line:
            return {
                "message": "Bus line not found",
                "data": None,
                "error": "Not found"
            }, 404
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
        station_line = StationLine(conn).update_station_line(
            bus_station_id, bus_line_id, data["seq"], data["start_time_first"], data["distance"])
        return jsonify({
            "message": "Successfully updated a station line",
            "data": station_line
        }), 201
    except Exception as e:
        return jsonify({
            "message": "failed to update a station line",
            "error": str(e),
            "data": None
        }), 400


@app.route("/bus_lines/<bus_line_id>/bus_stations/<bus_station_id>", methods=["DELETE"])
@cross_origin()
@jwt_required()
def delete_station_line(bus_station_id, bus_line_id):
    try:
        bus_line = BusLine(conn).get_bus_line_by_id(bus_line_id)
        if not bus_line:
            return {
                "message": "Bus line not found",
                "data": None,
                "error": "Not found"
            }, 404
        bus_station = BusStation(conn).get_bus_station_by_id(bus_station_id)
        if not bus_station:
            return {
                "message": "Bus station not found",
                "data": None,
                "error": "Not found"
            }, 404
        bus_station = StationLine(conn).delete_station_line(
            bus_station_id, bus_line_id)
        if bus_station:
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

# Routing


@app.route("/routes/shortest", methods=["GET"])
@cross_origin()
def get_shortest_path():
    try:
        start = int(request.args.get('start'))
        end = int(request.args.get('end'))
        shortest_path = StationLine(
            conn).shortest_path(start, end)
        return jsonify({
            "message": "Successfully retrieved shortest path",
            "data": shortest_path
        }), 200
    except Exception as e:
        return {
            "message": "Something went wrong",
            "error": str(e),
            "data": None
        }, 500


@app.route("/routes", methods=["GET"])
@cross_origin()
def get_find_all_paths():
    try:
        start = int(request.args.get('start'))
        end = int(request.args.get('end'))
        station_lines = StationLine(
            conn).find_all_paths(start, end)
        return jsonify({
            "message": "Successfully retrieved all paths",
            "data": station_lines
        }), 200
    except Exception as e:
        return {
            "message": "Something went wrong",
            "error": str(e),
            "data": None
        }, 500


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
