# -*- coding: utf-8 -*-
from datetime import datetime
import json
import logging
from odoo import _, models, fields
from odoo.exceptions import ValidationError
from odoo.addons.services.tools import evtc_service
from odoo.addons.evtc_lmfs.services.geotab_vehicle_service import REDIS_HOST, REDIS_DB, REDIS_PORT, REDIS_PWD, \
    REDIS_USR

logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @staticmethod
    def convert_to_datetime_before_write(value) -> datetime:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")

    @staticmethod
    def get_product_uom_domain(self,uom):
        return [uom.lower(), uom.upper(), uom.capitalize()]

    def get_trip_unit_cost(self):
        orderline_price = self.order_line.filtered(
            lambda line: line.product_uom.name in self.get_product_uom_domain('km'))
        return orderline_price.price_unit

    def _write_real_cost_trip(self, length):
        self.real_cost = self.get_trip_unit_cost() * length

    def write_order_datetime(self, values):
        values = values or {}
        if 'order_start_date' in values:
            self.order_start_date = datetime.now()
            del values['order_start_date']
        if 'order_stop_date' in values:
            self.order_stop_date = datetime.now()
            del values['order_stop_date']
        return values

    def set_order_request(self, values=None):
        collect_errors = {}
        if self.role_id.vehicle_id.geolocalization_type == 'geotab':
            return collect_errors
        values = self.write_order_datetime(values)
        for record in self:
            for key in values:
                try:
                    if record._fields[key].type == 'float':
                        record[key] = float(values[key])
                    elif record._fields[key].type == 'int':
                        record[key] = int(values[key])
                    elif record._fields[key].type == 'datetime':
                        record[key] = record.convert_to_datetime_before_write(values[key])
                    else:
                        record[key] = values[key]
                except Exception as error:
                    collect_errors[record._fields[key].name] = str(error)
                    logger.warning(
                        str(error)
                    )

        return collect_errors

    def update_info_trip_request(self):
        if self.odometer_start and self.odometer_stop:
            differences = self.odometer_stop - self.odometer_start
            self._write_real_cost_trip(differences)

    def vehicle_position(self, geotab):
        if 'lastTrack' in geotab and 'position' in geotab.get('lastTrack', {}):
            latitude = geotab['lastTrack']['position']['latitude']
            longitude = geotab['lastTrack']['position']['longitude']
        else:
            latitude = 0
            longitude = 0
        return latitude, longitude

    def end_course_geotab_vehicle(self):
        end_request = json.loads(
            self.get_vehicle_mo_details().text
        )
        vehicle_odometer = end_request.get('odometers', {})
        geotab = vehicle_odometer.get('GEOTAB', {})
        self.odometer_stop = geotab.get('value', 0)
        self.order_stop_date = datetime.now()
        lat, lng = self.vehicle_position(geotab)
        self.position_stop = "%s, %s" % (lat, lng)
        price_unit = self.get_trip_unit_cost()
        time_difference = self.order_stop_date - self.order_start_date
        hours = time_difference.seconds // 3600
        minutes = (time_difference.seconds % 3600) // 60
        fromatted_time = f"{hours:02d}.{minutes:02d}"
        self.real_duration = float(fromatted_time)
        self.real_distance = self.odometer_stop - self.odometer_start
        self.real_cost = self.real_distance * price_unit

    def get_immatriculation(self):
        licence = self.role_id.vehicle_id.license_plate
        return licence and licence.replace(' ', '').upper() or licence

    def get_vehicle_mo_details(self):
        mo = self.get_middle_office()
        immatriculation = self.get_immatriculation()
        response = mo.send_requests_to_mo(
            params=f"immatriculationID={immatriculation}",
            paramstypes="?",
            request="GET",
        )
        if response.status_code == 200:
            return response
        raise ValueError(_(
            'The request for get details failed'
        ))

    def start_course_geotab_vehicle(self):
        requests_rsp = json.loads(
            self.get_vehicle_mo_details().text
        )
        vehicle_odometer = requests_rsp.get('odometers', {})
        geotab = vehicle_odometer.get('GEOTAB', {})
        self.odometer_start = geotab.get('value', 0)
        self.order_start_date = datetime.now()
        lat, lng = self.vehicle_position(geotab)
        self.position_start = "%s, %s" %(lat, lng)

    def get_middle_office(self):
        mo = self.env['middle.office'].get_vehicle_details()
        if mo:
            return mo
        raise ValidationError(_('Vehicle API details required'))
