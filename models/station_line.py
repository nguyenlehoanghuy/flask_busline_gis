import heapq
import networkx as nx
import psycopg2


class StationLine:
    def __init__(self, conn):
        self.conn = conn

    def find_bus_lines_between_stations(self, start, end):
        """Find bus lines between start station and end station

        Args:
            start (int): start station id
            end (int): end station id

        Returns:
            array: id  array of bus lines
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "SELECT DISTINCT id_bus_line FROM station_line WHERE id_bus_station = %s OR id_bus_station = %s;", (start, end))
                station_lines = cursor.fetchall()
            return [{
                'id_bus_line': station_line[0],
            } for station_line in station_lines]
        except psycopg2.Error as e:
            print(
                f"Error fetching all station_line: {e}")
            return None

    def get_all_bus_stations_by_id_bus_line(self, id_bus_line):
        """Get all bus stations by bus line id, order by seq

        Args:
            id_bus_line (int): bus line id

        Returns:
            array: array of station lines
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM station_line WHERE id_bus_line = %s ORDER BY seq ASC;", (id_bus_line,))
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

    def init_graph(self, start, end):
        """Initialize graph of start, end station id

        Args:
            start (int): start station id
            end (int): end station id

        Returns:
            DiGraph: DiGraph of routing between start station and end station
        """
        G = nx.DiGraph()
        bus_lines = self.find_bus_lines_between_stations(start, end)
        for bus_line in bus_lines:
            stations = self.get_all_bus_stations_by_id_bus_line(
                bus_line['id_bus_line'])
            for station in stations:
                G.add_node(station['id_bus_station'])
            for i in range(len(stations) - 1):
                G.add_edge(stations[i]['id_bus_station'], stations[i + 1]
                           ['id_bus_station'], weight=stations[i]['distance'])
        return G

    def shortest_path(self, start, end):
        graph = self.init_graph(start, end)
        print(graph.edges)
        dist = {start: 0}
        previous = {}
        visited = set()
        heap = [(0, start)]

        while heap:
            (d, v) = heapq.heappop(heap)
            print(f"heap: {v}\n")
            if v in visited:
                continue
            visited.add(v)

            for neighbor, edge_attr in graph[v].items():
                weight = edge_attr['weight']
                print(f"weight: {weight}\n")
                distance = dist[v] + weight
                print(f"distance: {distance}\n")

                if neighbor not in dist or distance < dist[neighbor]:
                    dist[neighbor] = distance
                    previous[neighbor] = v
                    heapq.heappush(heap, (distance, neighbor))
        if end not in dist:
            print(f"No path found from {start} to {end}.")
            return None, float('inf')
        # Reconstruct path from start to end
        path = []
        current = end
        while current in previous:
            path.insert(0, current)
            current = previous[current]
        path.insert(0, start)

        return {"routing": path, "distance": dist[end]}
