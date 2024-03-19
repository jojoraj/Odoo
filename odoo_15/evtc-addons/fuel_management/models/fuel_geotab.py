from datetime import datetime, timedelta

from odoo import api, fields, models
from odoo.addons.services.tools import evtc_service
from odoo.tools import config

REDIS_HOST = config['redis_host']
REDIS_PORT = config['redis_port']
REDIS_PWD = config.get('redis_password', '')
REDIS_DB = config.get('redis_db', 0)
REDIS_USR = config.get('redis_user', '')


class FuelManagement(models.Model):
    _name = 'fuel.geotab'

    @api.model
    def get_fuel(self):
        gear_service_object = evtc_service.EvtcService(
            REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PWD, REDIS_USR
        )
        vehicle_ids = self.env['fleet.vehicle'].search(
            [('device_id', '!=', False)]).mapped('device_id')

        to_date = fields.datetime.now()
        from_date = fields.Datetime.to_string(
            datetime.today() - timedelta(days=30))
        time = fields.datetime.now()

        fuels = gear_service_object.get_fuel(vehicle_ids, time)
        volumes = gear_service_object.get_volume(vehicle_ids, from_date, to_date)

        dict_data_device = self._prepare_data_device(volumes, gear_service_object, vehicle_ids)

        for fuel in fuels:
            self._process_fuel(fuel, dict_data_device)

    @staticmethod
    def _prepare_data_device(volumes, gear_service_object, vehicle_ids):
        dict_data_device = {}
        for volume in volumes:
            for location_address_object in volume:
                moving_address = True
                location_object = location_address_object.get('location')
                lat = location_object.get('x', '')
                long = location_object.get('y', '')
                locations = gear_service_object.get_location(vehicle_ids, lat, long, moving_address)

                for location in locations:
                    get_list = location[0] if 0 < len(location) else {}
                    address = get_list.get('formattedAddress')
                    values = {
                        'derivedVolume': location_address_object.get('derivedVolume'),
                        'odometer': location_address_object.get('odometer'),
                        'dateTime': location_address_object.get('dateTime'),
                        'address': address,
                    }
                    device_id = location_address_object.get('device')['id']
                    dict_data_device.setdefault(device_id, []).append(values)

        return dict_data_device

    def _process_fuel(self, fuel, dict_data_device):
        if fuel:
            device_id = str(fuel[0]['device']['id'])
            vehicle = self.env['fleet.vehicle'].search([('device_id', '=', device_id)])

            vehicle_data = dict_data_device.get(device_id)
            if vehicle_data:
                for data in vehicle_data:
                    self._handle_vehicle_data(vehicle, data)

    def _handle_vehicle_data(self, vehicle, data):
        fuel_date = fields.Datetime.to_string(data['dateTime'])
        fuel_id = self.env["fleet.vehicle.fuel"].search([
            ("date", "=", fuel_date),
            ('vehicle_id', "=", vehicle.id)],
            limit=1
        )

        values = {
            'odometer': data['odometer'] / 1000,
            'vehicle_id': vehicle.id if vehicle else False,
            'volume': data['derivedVolume'],
            'address': data['address']
        }

        if fuel_id:
            fuel_id.update(values)
            card_fuel_id = self.env["fleet.card.fuel"].search([("date", "=", fields.Date.to_string(data['dateTime']))])
            if card_fuel_id:
                card_fuel_id.action_generate_geotab_qty()
        else:
            values['date'] = fuel_date
            self.env['fleet.vehicle.fuel'].sudo().create(values)
