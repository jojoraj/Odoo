from odoo import api, fields, models


class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    is_purchase = fields.Boolean(string="Is Purchase")
