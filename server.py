import os
import psycopg2

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required
from models import User
from utils import validate_email_and_password, validate_user
# from utils.validate import validate_book, validate_email_and_password, validate_user

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


@app.route("/users", methods=["GET"])
@cross_origin()
@jwt_required()
def gat_all_users():
    try:
        users = User(conn).get_all_users()
        return {
            "message": "Successfully gat all users",
            "data": users
        }, 201
    except Exception as e:
        return {
            "message": "Something went wrong",
            "error": str(e),
            "data": None
        }, 500

# @app.route("/books/", methods=["POST"])
# @token_required
# def add_book(current_user):
#     try:
#         book = dict(request.form)
#         if not book:
#             return {
#                 "message": "Invalid data, you need to give the book title, cover image, author id,",
#                 "data": None,
#                 "error": "Bad Request"
#             }, 400
#         if not request.files["cover_image"]:
#             return {
#                 "message": "cover image is required",
#                 "data": None
#             }, 400

#         book["image_url"] = request.host_url+"static/books/" + \
#             save_pic(request.files["cover_image"])
#         is_validated = validate_book(**book)
#         if is_validated is not True:
#             return {
#                 "message": "Invalid data",
#                 "data": None,
#                 "error": is_validated
#             }, 400
#         book = Books().create(**book, user_id=current_user["_id"])
#         if not book:
#             return {
#                 "message": "The book has been created by user",
#                 "data": None,
#                 "error": "Conflict"
#             }, 400
#         return jsonify({
#             "message": "successfully created a new book",
#             "data": book
#         }), 201
#     except Exception as e:
#         return jsonify({
#             "message": "failed to create a new book",
#             "error": str(e),
#             "data": None
#         }), 500


# @app.route("/books/", methods=["GET"])
# @token_required
# def get_books(current_user):
#     try:
#         books = Books().get_by_user_id(current_user["_id"])
#         return jsonify({
#             "message": "successfully retrieved all books",
#             "data": books
#         })
#     except Exception as e:
#         return jsonify({
#             "message": "failed to retrieve all books",
#             "error": str(e),
#             "data": None
#         }), 500


# @app.route("/books/<book_id>", methods=["GET"])
# @token_required
# def get_book(book_id):
#     try:
#         book = Books().get_by_id(book_id)
#         if not book:
#             return {
#                 "message": "Book not found",
#                 "data": None,
#                 "error": "Not Found"
#             }, 404
#         return jsonify({
#             "message": "successfully retrieved a book",
#             "data": book
#         })
#     except Exception as e:
#         return jsonify({
#             "message": "Something went wrong",
#             "error": str(e),
#             "data": None
#         }), 500


# @app.route("/books/<book_id>", methods=["PUT"])
# @token_required
# def update_book(current_user, book_id):
#     try:
#         book = Books().get_by_id(book_id)
#         if not book or book["user_id"] != current_user["_id"]:
#             return {
#                 "message": "Book not found for user",
#                 "data": None,
#                 "error": "Not found"
#             }, 404
#         book = request.form
#         if book.get('cover_image'):
#             book["image_url"] = request.host_url+"static/books/" + \
#                 save_pic(request.files["cover_image"])
#         book = Books().update(book_id, **book)
#         return jsonify({
#             "message": "successfully updated a book",
#             "data": book
#         }), 201
#     except Exception as e:
#         return jsonify({
#             "message": "failed to update a book",
#             "error": str(e),
#             "data": None
#         }), 400


# @app.route("/books/<book_id>", methods=["DELETE"])
# @token_required
# def delete_book(current_user, book_id):
#     try:
#         book = Books().get_by_id(book_id)
#         if not book or book["user_id"] != current_user["_id"]:
#             return {
#                 "message": "Book not found for user",
#                 "data": None,
#                 "error": "Not found"
#             }, 404
#         Books().delete(book_id)
#         return jsonify({
#             "message": "successfully deleted a book",
#             "data": None
#         }), 204
#     except Exception as e:
#         return jsonify({
#             "message": "failed to delete a book",
#             "error": str(e),
#             "data": None
#         }), 400


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
