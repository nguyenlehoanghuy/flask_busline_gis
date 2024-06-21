import psycopg2


class BusStation:
    def __init__(self, conn):
        self.conn = conn

    def get_all_bus_stations(self):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT * FROM bus_stations;")
                bus_stations = cursor.fetchall()
            return [{
                'id': bus_station[0],
                'name': bus_station[1],
                'long': bus_station[2],
                'lat': bus_station[3],
                'address': bus_station[4],
                'id_ward': bus_station[5]
            } for bus_station in bus_stations]
        except psycopg2.Error as e:
            print(f"Error fetching all users: {e}")
            return None

    def get_bus_station_by_id(self, bus_station_id):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM bus_stations WHERE id = %s;", (bus_station_id,))
                bus_station = cursor.fetchone()
                if not bus_station:
                    return None
            return {'id': bus_station[0], 'name': bus_station[1], 'long': bus_station[2], 'lat': bus_station[3], 'address': bus_station[4], 'id_ward': bus_station[5]}
        except psycopg2.Error as e:
            print(f"Error fetching user with id {bus_station_id}: {e}")
            return None

    def get_bus_station_by_name(self, name):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM bus_stations WHERE name = %s;", (name,))
                bus_station = cursor.fetchone()
                if not bus_station:
                    return None
            return {'id': bus_station[0], 'name': bus_station[1], 'long': bus_station[2], 'lat': bus_station[3], 'address': bus_station[4], 'id_ward': bus_station[5]}
        except psycopg2.Error as e:
            print(f"Error searching bus station by name {name}: {e}")
            return None

    def create_bus_station(self, name, long, lat, address, id_ward):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO bus_stations (name, long, lat, address, id_ward)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id;
                """, (name, long, lat, address, id_ward))
                new_bus_station_id = cursor.fetchone()[0]
                self.conn.commit()
            return {'id': new_bus_station_id}
        except psycopg2.Error as e:
            print(f"Error creating bus station: {e}")
            return None

    def update_bus_station(self, bus_station_id, name, long, lat, address, id_ward):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE bus_stations SET name = %s, long = %s, lat = %s, address = %s, id_ward = %s WHERE id = %s;
                """, (name, long, lat, address, id_ward, bus_station_id))
                self.conn.commit()
                return True
        except psycopg2.Error as e:
            print(f"Error updating user with id {bus_station_id}: {e}")
            return False

    def delete_bus_station(self, bus_station_id):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM bus_stations WHERE id = %s;", (bus_station_id,))
                self.conn.commit()
                return True
        except psycopg2.Error as e:
            print(f"Error deleting user with id {bus_station_id}: {e}")
            return False
