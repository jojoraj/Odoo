import mygeotab


class MyGeotabService:

    def __init__(self, username, database, server, session_id):
        self.client = mygeotab.API(username=username, database=database,
                                   server=server, session_id=session_id)

    def get_coordinates(self, addresses):
        coordinates = self.client.call('GetCoordinates', addresses=addresses)
        return coordinates

    def get_address(self, x, y):
        coordinates = self.client.call('GetAddresses', coordinates=[{"x": x, "y": y}])
        if coordinates and len(coordinates) > 0:
            res = coordinates[0]
            return res.get('formattedAddress')
        return "Unknown address"

    def get_directions(self, way_points):
        directions = self.client.call('GetDirections', waypoints=way_points)
        return directions

    def get_total_distance(self, device_id, from_date, to_date):
        distances = []
        trips = self.client.call('Get', typeName='Trip', search={'deviceSearch': {'id': device_id},
                                                                 'fromDate': from_date,
                                                                 'toDate': to_date})
        for trip in trips:
            distances.append(trip['distance'])
        return sum(distances)
