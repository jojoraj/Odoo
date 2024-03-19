from odoo import fields, models


class FleetVehicleModelCategory(models.Model):
    _inherit = 'fleet.vehicle.model.category'

    is_taxi = fields.Boolean()
    team_id = fields.Many2one('crm.team', 'Commercial team')
