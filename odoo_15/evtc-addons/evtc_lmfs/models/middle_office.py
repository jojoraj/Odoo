import requests
import json
from odoo import api, fields, models


class MiddleOffice(models.Model):
    _inherit = 'middle.office'

    service_type = fields.Selection(selection=
    [
        ('recommandation', 'Recommandation'),
        ('driver', 'Driver'),
        ('api_key', 'API Key'),
        ('opportunity', 'API access for Update fields in Opportunity'),
        ('create_trip', 'Create Trip'),
        ('create_vehicle', 'Create vehicle to MO')
    ], required=True, string="Service's type")
    api_key = fields.Char(required=False)
    endpoint = fields.Char('End Point', required=False)
    base_url = fields.Char(required=False)

    # replace method to pass params
    # @params: domain
    # @return relative mo
    @api.model
    def get_default_mo(self, domain=None):
        # TODO Add setting in company to specify default middle office
        return self.search(domain or [], limit=1)

    def get_default_create_vehicle(self):
        return self.search([
            ('service_type', '=', 'create_vehicle')
        ], limit=1)

    authorization_key = fields.Char("Authorization key")

    def get_full_url(self):
        return self.base_url + self.endpoint

    def send_vehicle_to_mo(self, payload):
        headers = {
            'Authorization': self.api_key,
            'Content-Type': 'application/json'
        }
        url = self.get_full_url()
        response = requests.request('POST', url, headers=headers, data=payload)
        return response
