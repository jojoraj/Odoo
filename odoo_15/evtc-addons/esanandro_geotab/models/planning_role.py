from odoo import fields, models


class PlanningRole(models.Model):
    _inherit = 'planning.role'

    vehicle_id = fields.Many2one(comodel_name='fleet.vehicle', string='Vehicle')
