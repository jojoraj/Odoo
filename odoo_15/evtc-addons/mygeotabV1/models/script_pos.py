import json
from time import gmtime, strftime


class DeviceOdometer():
    def __init__(self, redis, mygeotab):
        self.client = mygeotab
        self.r = redis

    def get_device_running(self):
        orders = self.r.get('orders')
        if orders:
            orders = json.loads(orders.decode().replace("\'", "\""))
            if orders:
                return [orders[key].get("device_id") for key in orders.keys()]
        return None

    def get_odoometer(self, device_ids):
        now = strftime("%Y-%m-%dT%H:%M:%SZ", gmtime())
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
                        'FromDate': now,
                        'ToDate': now
                    },
                }
            ))

        status_datas = self.client.multi_call(calls)

        if status_datas:
            values = {status_data[0].get("device").get("id"): {"odometer_2": status_data[0].get("data"),
                                                               "datetime_2": status_data[0].get("dateTime").strftime(
                                                                   "%Y-%m-%dT%H:%M:%SZ")} for status_data in
                      status_datas
                      }
            return values
        return None

    def set_device_odometers(self, data):
        orders = self.r.get('orders')
        if orders:
            orders = json.loads(orders.decode().replace("\'", "\""))
            if orders:
                for key in orders.keys():
                    device_id = orders[key].get("device_id")
                    orders[key]["odometer_2"] = data[device_id]["odometer_2"]
                    orders[key]["datetime_2"] = data[device_id]["datetime_2"]

            self.r.set("orders", str(orders))

    def execute(self):
        devices = self.get_device_running()
        if devices:
            datas = self.get_odoometer(devices)
            if datas:
                self.set_device_odometers(datas)
