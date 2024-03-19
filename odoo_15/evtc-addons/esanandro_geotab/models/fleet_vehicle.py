from odoo import fields, models


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    device_id = fields.Char()
    marker_color = fields.Char('Color')
