from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    date_igy = fields.Date(string="Date")

