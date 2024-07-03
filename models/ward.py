import psycopg2


class Ward:
    def __init__(self, conn):
        self.conn = conn

    def get_all_wards(self):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT * FROM wards;")
                wards = cursor.fetchall()
            return [{
                'id_ward': ward[0],
                'id_district': ward[1],
                'name': ward[2]
            } for ward in wards]
        except psycopg2.Error as e:
            print(f"Error fetching all wards: {e}")
            return None

    def get_ward_by_id(self, ward_id, district_id):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM wards WHERE id_ward = %s AND id_district = %s;", (ward_id, district_id))
                ward = cursor.fetchone()
                if not ward:
                    return None
            return {
                'id_ward': ward[0],
                'id_district': ward[1],
                'name': ward[2]
            }
        except psycopg2.Error as e:
            print(f"Error fetching ward with id {district_id, ward_id}: {e}")
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
                'id_ward': ward[0],
                'id_district': ward[1],
                'name': ward[2]
            }
        except psycopg2.Error as e:
            print(f"Error searching ward by name {name}: {e}")
            return None

    def create_ward(self, id_ward, id_district, name):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO wards (id_ward, id_district, name)
                    VALUES (%s, %s, %s)
                    RETURNING id_district, id_ward;
                """, (id_ward, id_district, name))
                new_ward_id = cursor.fetchone()
                self.conn.commit()
            return {'id_ward': new_ward_id[0], 'id_district': new_ward_id[1]}
        except psycopg2.Error as e:
            print(f"Error creating ward: {e}")
            return None

    def update_ward(self, ward_id, district_id, name):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE wards SET name = %s WHERE id_ward = %s AND id_district = %s;
                """, (name, ward_id, district_id))
                self.conn.commit()
                return True
        except psycopg2.Error as e:
            print(f"Error updating ward with id {district_id, ward_id}: {e}")
            return False

    def delete_ward(self, ward_id, district_id):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM wards WHERE id_ward = %s AND id_district = %s;", (ward_id, district_id))
                self.conn.commit()
                return True
        except psycopg2.Error as e:
            print(f"Error deleting ward with id {district_id, ward_id}: {e}")
            return False
