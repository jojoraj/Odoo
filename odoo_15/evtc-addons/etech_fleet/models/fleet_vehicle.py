# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class FleetVehicles(models.Model):
    _inherit = "fleet.vehicle"
    
    # add required field to the existing fields license_plate
    
    license_plate = fields.Char(required=True)