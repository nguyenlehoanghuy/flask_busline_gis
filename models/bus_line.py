import psycopg2


class BusLine:
    def __init__(self, conn):
        self.conn = conn

    def get_all_bus_lines(self):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT * FROM bus_lines;")
                bus_lines = cursor.fetchall()
                print(bus_lines)
            return [{
                'id': bus_line[0],
                'name': bus_line[1],
                'length': bus_line[2],
                'price': bus_line[3],
                'number_of_trips': bus_line[4],
                'time_between_trips': bus_line[5],
                'start_time_first': bus_line[6]
            } for bus_line in bus_lines]
        except psycopg2.Error as e:
            print(f"Error fetching all users: {e}")
            return None

    def get_bus_line_by_id(self, bus_line_id):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM bus_lines WHERE id = %s;", (bus_line_id,))
                bus_line = cursor.fetchone()
                if not bus_line:
                    return None
            return {
                'id': bus_line[0],
                'name': bus_line[1],
                'length': bus_line[2],
                'price': bus_line[3],
                'number_of_trips': bus_line[4],
                'time_between_trips': bus_line[5],
                'start_time_first': bus_line[6]
            }
        except psycopg2.Error as e:
            print(f"Error fetching user with id {bus_line_id}: {e}")
            return None

    def get_bus_line_by_name(self, name):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM bus_lines WHERE name = %s;", (name,))
                bus_line = cursor.fetchone()
                if not bus_line:
                    return None
            return {
                'id': bus_line[0],
                'name': bus_line[1],
                'length': bus_line[2],
                'price': bus_line[3],
                'number_of_trips': bus_line[4],
                'time_between_trips': bus_line[5],
                'start_time_first': bus_line[6]
            }
        except psycopg2.Error as e:
            print(f"Error searching bus station by name {name}: {e}")
            return None

    def create_bus_line(self, name, length, price, number_of_trips, time_between_trips, start_time_first):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO bus_lines (name, length, price, number_of_trips, time_between_trips, start_time_first)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id;
                """, (name, length, price, number_of_trips, time_between_trips, start_time_first))
                new_bus_line_id = cursor.fetchone()[0]
                self.conn.commit()
            return {'id': new_bus_line_id}
        except psycopg2.Error as e:
            print(f"Error creating bus station: {e}")
            return None

    def update_bus_line(self, bus_line_id, name, length, price, number_of_trips, time_between_trips, start_time_first):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE bus_lines SET name = %s, length = %s, price = %s, number_of_trips = %s, time_between_trips = %s, start_time_first = %s WHERE id = %s;
                """, (name, length, price, number_of_trips, time_between_trips, start_time_first, bus_line_id))
                self.conn.commit()
                return True
        except psycopg2.Error as e:
            print(f"Error updating user with id {bus_line_id}: {e}")
            return False

    def delete_bus_line(self, bus_line_id):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM bus_lines WHERE id = %s;", (bus_line_id,))
                self.conn.commit()
                return True
        except psycopg2.Error as e:
            print(f"Error deleting user with id {bus_line_id}: {e}")
            return False
