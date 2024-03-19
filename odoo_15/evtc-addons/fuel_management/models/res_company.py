from odoo import fields, models


class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    gap_alert = fields.Integer(default=0)
