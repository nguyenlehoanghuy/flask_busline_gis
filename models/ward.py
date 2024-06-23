import psycopg2


class Ward:
    def __init__(self, conn):
        self.conn = conn

    def get_all_wards(self):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT * FROM wards;")
                wards = cursor.fetchall()
                print(wards)
            return [{
                'id': ward[0],
                'name': ward[1],
                'id_district': ward[2]
            } for ward in wards]
        except psycopg2.Error as e:
            print(f"Error fetching all wards: {e}")
            return None

    def get_ward_by_id(self, ward_id):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM wards WHERE id = %s;", (ward_id,))
                ward = cursor.fetchone()
                if not ward:
                    return None
            return {
                'id': ward[0],
                'name': ward[1],
                'id_district': ward[2]
            }
        except psycopg2.Error as e:
            print(f"Error fetching ward with id {ward_id}: {e}")
            return None

    def get_ward_by_name(self, name):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM wards WHERE name = %s;", (name,))
                ward = cursor.fetchone()
                if not ward:
                    return None
            return {
                'id': ward[0],
                'name': ward[1],
                'id_district': ward[2]
            }
        except psycopg2.Error as e:
            print(f"Error searching ward by name {name}: {e}")
            return None

    def create_ward(self, name, id_district):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO wards (name, id_district)
                    VALUES (%s, %s)
                    RETURNING id;
                """, (name, id_district))
                new_ward_id = cursor.fetchone()[0]
                self.conn.commit()
            return {'id': new_ward_id}
        except psycopg2.Error as e:
            print(f"Error creating ward: {e}")
            return None

    def update_ward(self, ward_id, name, id_district):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE wards SET name = %s, id_district = %s WHERE id = %s;
                """, (name, id_district, ward_id))
                self.conn.commit()
                return True
        except psycopg2.Error as e:
            print(f"Error updating ward with id {ward_id}: {e}")
            return False

    def delete_ward(self, ward_id):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM wards WHERE id = %s;", (ward_id,))
                self.conn.commit()
                return True
        except psycopg2.Error as e:
            print(f"Error deleting ward with id {ward_id}: {e}")
            return False
