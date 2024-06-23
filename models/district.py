import psycopg2


class District:
    def __init__(self, conn):
        self.conn = conn

    def get_all_districts(self):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT * FROM districts;")
                districts = cursor.fetchall()
            return [{
                'id': district[0],
                'name': district[1]
            } for district in districts]
        except psycopg2.Error as e:
            print(f"Error fetching all districts: {e}")
            return None

    def get_district_by_id(self, district_id):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM districts WHERE id = %s;", (district_id,))
                district = cursor.fetchone()
                if not district:
                    return None
            return {
                'id': district[0],
                'name': district[1]
            }
        except psycopg2.Error as e:
            print(f"Error fetching district with id {district_id}: {e}")
            return None

    def get_district_by_name(self, name):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM districts WHERE name = %s;", (name,))
                district = cursor.fetchone()
                if not district:
                    return None
            return {
                'id': district[0],
                'name': district[1]
            }
        except psycopg2.Error as e:
            print(f"Error searching district by name {name}: {e}")
            return None

    def create_district(self, name):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO districts (name)
                    VALUES (%s)
                    RETURNING id;
                """, (name,))
                new_district_id = cursor.fetchone()[0]
                self.conn.commit()
            return {'id': new_district_id}
        except psycopg2.Error as e:
            print(f"Error creating district: {e}")
            return None

    def update_district(self, district_id, name):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE districts SET name = %s WHERE id = %s;
                """, (name,  district_id))
                self.conn.commit()
                return True
        except psycopg2.Error as e:
            print(f"Error updating district with id {district_id}: {e}")
            return False

    def delete_district(self, district_id):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM districts WHERE id = %s;", (district_id,))
                self.conn.commit()
                return True
        except psycopg2.Error as e:
            print(f"Error deleting district with id {district_id}: {e}")
            return False
