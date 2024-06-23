import psycopg2


class StationLine:
    def __init__(self, conn):
        self.conn = conn

    def get_all_bus_stations_by_id_bus_line(self, id_bus_line):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM station_line WHERE id_bus_line = %s;", (id_bus_line,))
                station_lines = cursor.fetchall()
            return [{
                'id_bus_station': station_line[0],
                'id_bus_line': station_line[1],
                'seq': station_line[2],
                'start_time_first': station_line[3],
                'distance': station_line[4]
            } for station_line in station_lines]
        except psycopg2.Error as e:
            print(
                f"Error fetching station_line with bus line id {id_bus_line}: {e}")
            return None

    def get_all_bus_lines_by_id_bus_station(self, id_bus_station):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM station_line WHERE id_bus_station = %s;", (id_bus_station,))
                station_lines = cursor.fetchall()
            return [{
                'id_bus_station': station_line[0],
                'id_bus_line': station_line[1],
                'seq': station_line[2],
                'start_time_first': station_line[3],
                'distance': station_line[4]
            } for station_line in station_lines]
        except psycopg2.Error as e:
            print(
                f"Error fetching station_line with bus station id {id_bus_station}: {e}")
            return None

    def create_station_line(self, id_bus_station, id_bus_line, seq, start_time_first, distance):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO station_line (id_bus_station, id_bus_line, seq, start_time_first, distance)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id_bus_station, id_bus_line;
                """, (id_bus_station, id_bus_line, seq, start_time_first, distance))
                new_station_line_id = cursor.fetchone()
                self.conn.commit()
            return {'id_bus_station': new_station_line_id[0], 'id_bus_line': new_station_line_id[1]}
        except psycopg2.Error as e:
            print(f"Error creating bus station: {e}")
            return None

    def update_station_line(self, id_bus_station, id_bus_line, seq, start_time_first, distance):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE station_line SET seq = %s, start_time_first = %s, distance = %s WHERE id_bus_station = %s AND id_bus_line = %s;
                """, (seq, start_time_first, distance, id_bus_station, id_bus_line))
                self.conn.commit()
                return True
        except psycopg2.Error as e:
            print(
                f"Error updating station_line with id {id_bus_station, id_bus_line}: {e}")
            return False

    def delete_station_line(self, id_bus_station, id_bus_line):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM station_line WHERE id_bus_station = %s AND id_bus_line = %s;", (id_bus_station, id_bus_line))
                self.conn.commit()
                return True
        except psycopg2.Error as e:
            print(
                f"Error deleting station_line with id {id_bus_station, id_bus_line}: {e}")
            return False
