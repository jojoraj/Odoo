from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    gap_alert = fields.Integer(related="company_id.gap_alert", readonly=False)
