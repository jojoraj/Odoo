from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    logo_all = fields.Binary('Logo invoice and sale order')
