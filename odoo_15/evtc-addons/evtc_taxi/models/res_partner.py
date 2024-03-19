import hashlib
import json

from odoo import fields, models
from odoo.http import request


class ResPartner(models.Model):
    _inherit = 'res.partner'

    secret_key = fields.Char()
    state_vehicle_id = fields.Many2one('fleet.vehicle.state')
    external_diver = fields.Boolean()
    driver_cin = fields.Char()
    license_expired_date = fields.Date()
    authorization_expired_date = fields.Date()

    def write(self, values):
        res = super().write(values)
        if values.get('external_diver', False):
            self.mo_add_driver()
        return res

    def generate_secret_key(self) -> str:
        return hashlib.sha256(f'{self.create_date}-{self.name}'.encode('utf-8')).hexdigest()

    def get_formatted_phone(self):
        return self.phone.replace(' ', '').strip() if self.phone else ''

    def mo_add_client(self):
        middle_office_id = self.env['middle.office'].get_default_mo()
        payload = json.dumps({
            'firstName': self.name,
            'phoneNumber': self.get_formatted_phone()
        })
        return middle_office_id.add_client(payload)

    def mo_add_driver(self):
        if self.external_diver:
            middle_office_id = self.env['middle.office'].get_default_mo()
            vehicle = middle_office_id.get_specific_vehicle(self.get_formatted_phone())
            if vehicle.status_code == 404:
                secret = self.generate_secret_key()
                values = {
                    'secretPassword': secret,
                    'driverName': self.name,
                    'driverPhone': self.get_formatted_phone(),
                    'status': 'UNAVAILABLE',
                }
                for item in ['128', '256', '512', '1920']:
                    values.update({
                        f'image_{item}': f'{request.httprequest.host_url}/web/image/res.partner/{self.id}/image_{item}'
                    })
                payload = json.dumps(values)
                self.write({'secret_key': secret})
                return middle_office_id.add_vehicle(payload)
            else:
                self.write({
                    'secret_key': vehicle.json()['secretPassword']
                })
                return vehicle
