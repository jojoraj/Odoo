# Part of Odoo. See LICENSE file for full copyright and licensing details.
import ast
import logging
import json
import time

from odoo import models, fields, api, _ ,SUPERUSER_ID
from odoo.exceptions import ValidationError, UserError
from odoo.addons.evtc_lmfs.middle_office_service import middle_office_service

import redis
from odoo.tools import config

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    geolocalization_type = fields.Selection([
    ('lmfs', 'Last Mille'),
    ('geotab', 'Geotab')
    ], string="Localization Device Type")

    vehicle_mo_state = fields.Selection(related="state_id.middle_office_value", string="Middle office state")



    def create_mo_vehicle(self):
        mo_data = self.get_mo_json_values()
        mo_default = self.env['middle.office'].search([('type', '=', 'create_vehicle')],limit=1)
        response = False
        if mo_default:
            response = mo_default.send_requests_to_mo(mo_data)
            if response.status_code != 200:
                raise ValidationError(_('requests failed, please see log for more details'))
        return response

    def update_state_vehicle_mo(self, license_plate, status):
        mo_default = self.env['middle.office'].search([('type', '=', 'update_state_vehicle')],limit=1)
        response = False
        mo_data = json.dumps({
            "immatriculation": license_plate, 
            "status": status
        })
        if mo_default:
            response = mo_default.send_requests_to_mo(mo_data)
            if response.status_code != 200:
                raise ValidationError(_('requests failed, please see log for more details'))
        return response

    def get_mo_json_values(self):
        vehicle_id = self.license_plate.replace(' ', '').upper() if self.license_plate else ""
        return json.dumps({
            "immatriculationID": vehicle_id,
            "vehicleId ": vehicle_id,
            "status": self.state_id.middle_office_value if self.state_id else "",
            "bearing": 0,
            "characteristic": {
                "brand": self.brand_id.name if self.brand_id else "",
                "color": self.color or "",
                "numberOfPlaces": self.seats,
                "typeTrack": self.geolocalization_type.upper() if self.geolocalization_type else ''
            },
        })

    def get_vehicle_sync_fields(self):
        return [
            'license_plate',
            'state_id',
            'brand_id',
            'color',
            'seats'
        ]


    def get_vehicle_sync_field_write(self):
        return [
            'license_plate',
            'geolocalization_type'
        ]


    def sync_multiple_vehicle_to_mo(self):
        for vehicle in self:
            vehicle.with_user(SUPERUSER_ID).create_mo_vehicle()

    def write(self, values):
        super(FleetVehicle, self).write(values)
        if any(element in values for element in self.get_vehicle_sync_field_write()) and self.env['fleet.vehicle'].browse(self.id).exists():
            self.create_mo_vehicle()
        if 'state_id' in values:
            previous_state = self.state_id
            new_state = values['state_id']
            if previous_state != new_state:
                self.update_state_vehicle_mo(self.license_plate, self.vehicle_mo_state)

        
    @api.model_create_multi
    def create(self, values):
        to_found = isinstance(values, list) and values[0] or values
        vehicle_id = super(FleetVehicle, self).create(values)
        if any(element in to_found for element in self.get_vehicle_sync_fields()):
            vehicle_id.create_mo_vehicle()
        return vehicle_id
