import mygeotab
from odoo.tools import config

REDIS_HOST = config['redis_host']
REDIS_PORT = config['redis_port']
REDIS_PWD = config.get('redis_password', '')
REDIS_DB = config.get('redis_db', 0)
REDIS_USR = config.get('redis_user', '')


class MyGeotabServiceFuel:

    def __init__(self, username, database, server, session_id):
        self.client = mygeotab.API(username=username, server=server, database=database, session_id=session_id)

    def get_volume(self, device_ids, fromdate, todate):
        call = []
        for device_id in device_ids:
            call.append((
                "Get",
                {
                    "typeName": "FuelUpEvent",
                    "search": {
                        "deviceSearch": {
                            "id": device_id
                        },
                        'FromDate': fromdate,
                        'ToDate': todate
                    },
                }
            ))
        volume = self.client.multi_call(call)
        return volume

    def get_fuel(self, device_ids, time):
        calls = []
        for device_id in device_ids:
            calls.append((
                "Get",
                {
                    "typeName": "StatusData",
                    "search": {
                        "diagnosticSearch": {
                            "id": "DiagnosticOdometerAdjustmentId"
                        },
                        "deviceSearch": {
                            "id": device_id
                        },
                        'FromDate': time,
                        'ToDate': time
                    },
                }
            ))
        fuels = self.client.multi_call(calls)
        return fuels

    def get_location(self, device_ids, lat, long, movingAddresses):
        loc = []
        for _device_id in device_ids:
            loc.append(("GetAddresses",
                       {
                           "coordinates": [{
                               "x": lat,
                               "y": long
                           }],
                           "movingAddresses": movingAddresses
                       }))
            locations = self.client.multi_call(loc)
            return locations
