import psycopg2

from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash


class User:
    def __init__(self, conn):
        self.conn = conn

    def get_all_users(self):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users;")
                users = cursor.fetchall()
            return [{'id': user[0], 'email': user[1], 'name': user[2], 'password': user[3]} for user in users]
        except psycopg2.Error as e:
            print(f"Error fetching all users: {e}")
            return None

    def get_user_by_id(self, user_id):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM users WHERE id = %s;", (user_id,))
                user = cursor.fetchone()
            return {'id': user[0], 'email': user[1], 'name': user[2], 'password': user[3]}
        except psycopg2.Error as e:
            print(f"Error fetching user with id {user_id}: {e}")
            return None

    def create_user(self, email, name, password):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO users (name, email, password)
                    VALUES (%s, %s, %s)
                    RETURNING id;
                """, (name, email, self.encrypt_password(password)))
                new_user_id = cursor.fetchone()[0]
                self.conn.commit()
                access_token = create_access_token(
                    identity=new_user_id)
            return {
                "access_token": access_token,
                "token_type": "bearer",
            }
        except psycopg2.Error as e:
            print(f"Error creating user: {e}")
            return None

    def update_user(self, user_id, email, name, password):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE users SET email = %s, name = %s, password = %s WHERE id = %s;
                """, (email, name, self.encrypt_password(password), user_id))
                self.conn.commit()
                return True
        except psycopg2.Error as e:
            print(f"Error updating user with id {user_id}: {e}")
            return False

    def delete_user(self, user_id):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("DELETE FROM users WHERE id = %s;", (user_id,))
                self.conn.commit()
                return True
        except psycopg2.Error as e:
            print(f"Error deleting user with id {user_id}: {e}")
            return False

    def get_user_by_email(self, email):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM users WHERE email = %s;", (email,))
                user = cursor.fetchone()
            return {'id': user[0], 'email': user[1], 'name': user[2], 'password': user[3]}
        except psycopg2.Error as e:
            print(f"Error fetching user with id {email}: {e}")
            return None

    def encrypt_password(self, password):
        """Encrypts the password using a secure hash function."""
        return generate_password_hash(password)

    def login(self, email, password):
        """Attempts to log in a user with the provided email and password."""
        user = self.get_user_by_email(email)
        if not user or not check_password_hash(user["password"], password):
            return None
        access_token = create_access_token(
            identity=user['id'])
        return {
            "access_token": access_token,
            "token_type": "bearer",
        }
