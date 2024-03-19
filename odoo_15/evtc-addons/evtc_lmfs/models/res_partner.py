from odoo import _, models, fields, api, SUPERUSER_ID
from odoo.exceptions import UserError
import requests
import json
import logging

logger = logging.getLogger('logger_script_python')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_driver = fields.Boolean("Is driver")
   
    def get_mo_vehicle(self):
        driver_mo = self.env['middle.office'].get_default_mo_driver_vehicle()
        if driver_mo:
            return driver_mo
        raise ValueError(_("The Driver api url is not set, call the administrator to fix it !"))

    def get_mo_driver(self):
        mo = self.env['middle.office'].get_default_mo_driver()
        if mo:
            return mo
        raise ValueError(_("The Driver api url is not set, call the administrator to fix it !"))

    def sync_partner(self, payload):
        mo = self.get_mo_driver()
        driver_payload = json.dumps(payload)
        driver_data = mo.send_requests_to_mo(payload=driver_payload)
        if driver_data.status_code != 200:
            logger.error(f"Request failed with status code: {driver_data.status_code} - {driver_data.reason}")
        return driver_data.status_code == 200

    def sync_vehicle_driver(self, phone):
        mo = self.get_mo_vehicle()
        vehicle_data = mo.send_requests_to_mo(params=phone)
        if vehicle_data.status_code != 200:
            logger.error(f"Request failed with status code: {vehicle_data.status_code} - {vehicle_data.reason}")
        return vehicle_data.status_code == 200

    @staticmethod
    def get_formatted_phone(phone):
        if not phone:
            raise UserError(_("Mobile or Phone must be present in form"))
        return phone.replace(' ', '').strip() if phone else ''

    @staticmethod
    def convert_key(data):
        return {
            'driverPhone': data.get('name'),
            "driverName": data.get('phone'),
            "driverPicture": data.get('driverPicture')
        }

    def get_payload(self):
        return {
            "name": self.name,
            "phone": self.get_formatted_phone(self.phone or self.mobile),
            'driverPicture': self.env['ir.config_parameter'].get_param(
                'web.base.url') + f"/website/image/res.partner/{self.id}/image_1920"
        }

    def sync_payload(self):
        payload = self.get_payload()
        self.sync_partner(
            self.convert_key(payload)
        )
        self.sync_vehicle_driver(
            payload['phone']
        )

    def write(self, values):
        required_fields = ['name', 'image_1920', 'phone', 'is_driver']
        to_update = False
        for f in required_fields:
            if f in values:
                to_update = True
        super(ResPartner, self).write(values)
        if to_update:
            self.sync_payload()

    @api.model_create_multi
    def create(self, vals_list):
        result = super(ResPartner, self).create(vals_list)
        if result.is_driver:
            result.sync_payload()
        return result


    is_b2b = fields.Boolean(string="Is client B2B")
    
    related_company = fields.Many2one('res.partner', string='Related Company', index=True)

